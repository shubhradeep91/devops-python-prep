import boto3
import logging
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_ec2_client():
    """Initializes and returns the EC2 client."""
    return boto3.client('ec2')

def lambda_handler(event, context):
    """
    Lambda function entry point.
    Identifies unused EBS snapshots and their corresponding volumes for cleanup.
    """
    ec2_client = get_ec2_client()
    deleted_snapshots = []
    deleted_volumes = []
    kept_resources = []
    
    try:
        # 1. Identify existing snapshots owned by the account
        logger.info("Starting EBS Snapshot scan...")
        
        # Use OwnerIds=['self'] to only list snapshots owned by the current AWS account.
        response = ec2_client.describe_snapshots(OwnerIds=['self'])
        snapshots = response.get('Snapshots', [])
        
        if not snapshots:
            logger.info("No snapshots found owned by this account.")
            return {
                'statusCode': 200,
                'body': 'No snapshots found to process.'
            }

        logger.info(f"Found {len(snapshots)} snapshots to process.")
        
        for snapshot in snapshots:
            snapshot_id = snapshot['SnapshotId']
            volume_id = snapshot.get('VolumeId')
            
            logger.info(f"\nProcessing Snapshot ID: {snapshot_id}")
            
            # 2. Check if a volume is attached to the snapshot
            if not volume_id:
                # Case 1: Snapshot has no VolumeId (might be an old, manually created, or truly orphaned snapshot)
                logger.warning(f"Snapshot {snapshot_id} has no associated VolumeId. Deleting it.")
                try:
                    ec2_client.delete_snapshot(SnapshotId=snapshot_id)
                    deleted_snapshots.append(snapshot_id)
                    logger.info(f"SUCCESS: Deleted snapshot {snapshot_id}.")
                except ClientError as e:
                    logger.error(f"ERROR deleting snapshot {snapshot_id}: {e}")
                continue # Move to the next snapshot
            
            # Case 2: Snapshot has a VolumeId. Now check the status of that volume.
            volume_id = volume_id
            
            try:
                volume_response = ec2_client.describe_volumes(VolumeIds=[volume_id])
                volumes = volume_response.get('Volumes', [])
                
                if not volumes:
                    # The volume ID exists in the snapshot metadata, but the volume itself is gone (manually deleted).
                    # This is essentially an orphaned snapshot, safe to delete.
                    logger.warning(f"Volume {volume_id} not found. Deleting snapshot {snapshot_id}.")
                    ec2_client.delete_snapshot(SnapshotId=snapshot_id)
                    deleted_snapshots.append(snapshot_id)
                    logger.info(f"SUCCESS: Deleted snapshot {snapshot_id}.")
                    continue
                
                volume = volumes[0]
                attachments = volume.get('Attachments', [])
                
                # Check if the volume is attached to an EC2 instance
                if attachments:
                    # The volume is attached to an EC2 instance (e.g., in use)
                    instance_id = attachments[0]['InstanceId']
                    logger.info(f"Volume {volume_id} is attached to EC2 instance {instance_id}. Keeping snapshot/volume.")
                    kept_resources.append({
                        'SnapshotId': snapshot_id,
                        'VolumeId': volume_id,
                        'InstanceId': instance_id
                    })
                else:
                    # The volume is not attached to an instance (e.g., status is 'available'). It's unused.
                    logger.info(f"Volume {volume_id} is not attached to any EC2 instance (Status: {volume.get('State')}). Deleting snapshot and volume.")
                    
                    # 2.a. Delete the Snapshot
                    ec2_client.delete_snapshot(SnapshotId=snapshot_id)
                    deleted_snapshots.append(snapshot_id)
                    logger.info(f"SUCCESS: Deleted snapshot {snapshot_id}.")
                    
                    # 2.b. Delete the Volume
                    ec2_client.delete_volume(VolumeId=volume_id)
                    deleted_volumes.append(volume_id)
                    logger.info(f"SUCCESS: Deleted volume {volume_id}.")
            
            except ClientError as e:
                # Handle cases where the volume is invalid or another error occurs during volume lookup/deletion
                if e.response['Error']['Code'] == 'InvalidVolume.NotFound':
                    logger.warning(f"Volume {volume_id} not found during lookup. Deleting snapshot {snapshot_id}.")
                    try:
                        ec2_client.delete_snapshot(SnapshotId=snapshot_id)
                        deleted_snapshots.append(snapshot_id)
                        logger.info(f"SUCCESS: Deleted snapshot {snapshot_id}.")
                    except ClientError as delete_e:
                        logger.error(f"ERROR deleting orphaned snapshot {snapshot_id}: {delete_e}")
                else:
                    logger.error(f"ERROR processing volume {volume_id} for snapshot {snapshot_id}: {e}")
        
    except ClientError as e:
        logger.error(f"FATAL ERROR during snapshot description: {e}")
        return {
            'statusCode': 500,
            'body': f"Error listing snapshots: {e}"
        }
        
    summary = {
        'deleted_snapshots': deleted_snapshots,
        'deleted_volumes': deleted_volumes,
        'kept_resources': kept_resources
    }

    logger.info("--- Cleanup Summary ---")
    logger.info(f"Snapshots Deleted: {len(deleted_snapshots)}")
    logger.info(f"Volumes Deleted: {len(deleted_volumes)}")
    logger.info(f"Resources Kept: {len(kept_resources)}")
    logger.info("-----------------------")
    
    return {
        'statusCode': 200,
        'body': summary
    }