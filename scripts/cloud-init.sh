#!/bin/bash
DISK_DEVICE="/dev/sdc"
MOUNT_POINT="/mnt/models"

# Format if needed
if ! blkid $DISK_DEVICE; then
  mkfs.ext4 $DISK_DEVICE
fi

# Make mount point and mount it
mkdir -p $MOUNT_POINT
mount $DISK_DEVICE $MOUNT_POINT

# Give ownership to azureuser
chown -R azureuser:azureuser "$MOUNT_POINT"
chmod 700 "$MOUNT_POINT"
