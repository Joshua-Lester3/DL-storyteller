#!/bin/bash
set -euxo pipefail
exec > /var/log/cloud-init-user.log 2>&1

DISK_DEVICE="/dev/sdc"
MOUNT_POINT="/mnt/models"

# Format if needed
if ! blkid $DISK_DEVICE; then
  mkfs.ext4 $DISK_DEVICE
fi

# Make mount point and mount it
mkdir -p $MOUNT_POINT
mount $DISK_DEVICE $MOUNT_POINT

# Add to /etc/fstab for automatic remount
echo "/dev/sdc /mnt/models ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab

# Give ownership to azureuser
chown -R azureuser:azureuser "$MOUNT_POINT"
chmod 700 "$MOUNT_POINT"

touch /var/log/cloud-init-done.marker
