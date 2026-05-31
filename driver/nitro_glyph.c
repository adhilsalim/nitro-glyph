#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/uaccess.h>
#include <linux/ioctl.h>
#include <linux/acpi.h>
#include <linux/wmi.h>
#include <linux/errno.h>

#include "nitro_glyph.h"

#define DEVICE_NAME "nitro-glyph"
#define CLASS_NAME "nitro-glyph"
#define WMID_GUID4 "7A4DDFE7-5B5D-40B4-8595-4408E0CC7F56"

#define ACER_WMID_SET_GAMING_LED_METHODID 2
#define ACER_WMID_GET_GAMING_SYS_INFO_METHODID 5
#define ACER_WMID_SET_GAMING_STATIC_LED_METHODID 6
#define ACER_WMID_SET_GAMINGKBBL_METHODID 20

static dev_t nitro_dev;
static struct cdev nitro_cdev;
static struct class *nitro_class;

struct nitro_fw_zone
{
    u8 zone;
    u8 red;
    u8 green;
    u8 blue;
} __packed;

static u8 nitro_zone_to_fw(u8 zone)
{
    switch (zone)
    {
    case 1:
        return 1;

    case 2:
        return 2;

    case 3:
        return 4;

    case 4:
        return 8;

    default:
        return 0;
    }
}

static char *nitro_devnode(
    const struct device *dev,
    umode_t *mode)
{
    if (mode)
        *mode = 0666;

    return NULL;
}

static int nitro_set_effect(
    const struct nitro_effect *effect);

static int nitro_open(struct inode *inode, struct file *file)
{
    pr_info("nitro_glyph: device opened\n");
    return 0;
}

static int nitro_release(struct inode *inode, struct file *file)
{
    pr_info("nitro_glyph: device closed\n");
    return 0;
}

static int nitro_enable(void)
{
    acpi_status status;
    u64 enable_payload;

    pr_info("nitro_glyph: querying gaming sysinfo\n");

    status = wmi_evaluate_method(
        WMID_GUID4,
        0,
        ACER_WMID_GET_GAMING_SYS_INFO_METHODID,
        NULL,
        NULL);

    pr_info(
        "nitro_glyph: sysinfo status=%d\n",
        status);

    enable_payload = 8ULL | (15ULL << 40);

    {
        struct acpi_buffer input = {
            sizeof(enable_payload),
            &enable_payload};

        status = wmi_evaluate_method(
            WMID_GUID4,
            0,
            ACER_WMID_SET_GAMING_LED_METHODID,
            &input,
            NULL);

        pr_info(
            "nitro_glyph: enable status=%d\n",
            status);
    }

    if (ACPI_FAILURE(status))
        return -EIO;

    return 0;
}

static int nitro_set_zone(
    const struct nitro_zone *zone)
{
    acpi_status status;

    struct nitro_fw_zone fw = {
        .zone = nitro_zone_to_fw(zone->zone),
        .red = zone->red,
        .green = zone->green,
        .blue = zone->blue};

    struct acpi_buffer input = {
        sizeof(fw),
        &fw};

    if (!fw.zone)
        return -EINVAL;

    status = wmi_evaluate_method(
        WMID_GUID4,
        0,
        ACER_WMID_SET_GAMING_STATIC_LED_METHODID,
        &input,
        NULL);

    pr_info(
        "nitro_glyph: zone=%u r=%u g=%u b=%u status=%d\n",
        zone->zone,
        zone->red,
        zone->green,
        zone->blue,
        status);

    return ACPI_FAILURE(status) ? -EIO : 0;
}

static int nitro_set_effect(
    const struct nitro_effect *effect)
{
    acpi_status status;
    u8 payload[16] = {0};

    if (effect->mode > NITRO_ZOOM)
        return -EINVAL;

    if (effect->brightness > 100)
        return -EINVAL;

    if (effect->speed > 12)
        return -EINVAL;

    if (effect->direction > 2)
        return -EINVAL;

    payload[0] = effect->mode;
    payload[1] = effect->speed;
    payload[2] = effect->brightness;
    payload[4] = effect->direction;

    payload[5] = effect->red;
    payload[6] = effect->green;
    payload[7] = effect->blue;

    payload[9] = 1;

    if (effect->mode == NITRO_WAVE)
        payload[3] = 8;

    {
        struct acpi_buffer input = {
            sizeof(payload),
            payload};

        status = wmi_evaluate_method(
            WMID_GUID4,
            0,
            ACER_WMID_SET_GAMINGKBBL_METHODID,
            &input,
            NULL);

        if (ACPI_FAILURE(status))
            return -EIO;
    }

    pr_info(
        "nitro_glyph: effect mode=%u speed=%u bright=%u status=%d\n",
        effect->mode,
        effect->speed,
        effect->brightness,
        status);

    return ACPI_FAILURE(status) ? -EIO : 0;
}

static int nitro_disable(void)
{
    struct nitro_effect effect = {
        .mode = NITRO_STATIC,
        .brightness = 0};

    return nitro_set_effect(&effect);
}

static long nitro_ioctl(
    struct file *file,
    unsigned int cmd,
    unsigned long arg)
{
    switch (cmd)
    {

    case NITRO_IOCTL_ENABLE:
        return nitro_enable();

    case NITRO_IOCTL_DISABLE:
        return nitro_disable();

    case NITRO_IOCTL_SET_ZONE:
    {
        struct nitro_zone zone;

        if (copy_from_user(
                &zone,
                (void __user *)arg,
                sizeof(zone)))
            return -EFAULT;

        return nitro_set_zone(&zone);
    }

    case NITRO_IOCTL_SET_EFFECT:
    {
        struct nitro_effect effect;

        if (copy_from_user(
                &effect,
                (void __user *)arg,
                sizeof(effect)))
            return -EFAULT;

        return nitro_set_effect(&effect);
    }

    default:
        return -EINVAL;
    }
}

static const struct file_operations nitro_fops = {
    .owner = THIS_MODULE,
    .open = nitro_open,
    .release = nitro_release,
    .unlocked_ioctl = nitro_ioctl,
#ifdef CONFIG_COMPAT
    .compat_ioctl = nitro_ioctl,
#endif
};

static int __init nitro_init(void)
{
    int ret;

    ret = alloc_chrdev_region(
        &nitro_dev,
        0,
        1,
        DEVICE_NAME);

    if (ret)
        return ret;

    cdev_init(&nitro_cdev, &nitro_fops);

    ret = cdev_add(
        &nitro_cdev,
        nitro_dev,
        1);

    if (ret)
    {
        unregister_chrdev_region(nitro_dev, 1);
        return ret;
    }

    nitro_class = class_create(CLASS_NAME);

    if (IS_ERR(nitro_class))
    {
        cdev_del(&nitro_cdev);
        unregister_chrdev_region(nitro_dev, 1);
        return PTR_ERR(nitro_class);
    }

    nitro_class->devnode = nitro_devnode;

    if (IS_ERR(device_create(
            nitro_class,
            NULL,
            nitro_dev,
            NULL,
            DEVICE_NAME)))
    {

        class_destroy(nitro_class);
        cdev_del(&nitro_cdev);
        unregister_chrdev_region(nitro_dev, 1);
        return -ENOMEM;
    }

    nitro_enable();
    pr_info("nitro_glyph: loaded\n");
    return 0;
}

static void __exit nitro_exit(void)
{
    device_destroy(
        nitro_class,
        nitro_dev);

    class_destroy(nitro_class);

    cdev_del(&nitro_cdev);

    unregister_chrdev_region(
        nitro_dev,
        1);

    pr_info("nitro_glyph: unloaded\n");
}

module_init(nitro_init);
module_exit(nitro_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Adhil Salim");
MODULE_DESCRIPTION("Nitro Glyph Driver");