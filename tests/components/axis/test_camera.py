"""Axis camera platform tests."""

from unittest.mock import patch

import pytest

from homeassistant.components import camera
from homeassistant.components.axis.const import (
    CONF_STREAM_PROFILE,
    DOMAIN as AXIS_DOMAIN,
)
from homeassistant.components.camera import DOMAIN as CAMERA_DOMAIN
from homeassistant.const import STATE_IDLE
from homeassistant.setup import async_setup_component

from .conftest import NAME
from .test_device import setup_axis_integration


async def test_platform_manually_configured(hass):
    """Test that nothing happens when platform is manually configured."""
    assert (
        await async_setup_component(
            hass, CAMERA_DOMAIN, {CAMERA_DOMAIN: {"platform": AXIS_DOMAIN}}
        )
        is True
    )

    assert AXIS_DOMAIN not in hass.data


async def test_camera(hass, config_entry):
    """Test that Axis camera platform is loaded properly."""
    await setup_axis_integration(hass, config_entry)

    assert len(hass.states.async_entity_ids(CAMERA_DOMAIN)) == 1

    entity_id = f"{CAMERA_DOMAIN}.{NAME}"

    cam = hass.states.get(entity_id)
    assert cam.state == STATE_IDLE
    assert cam.name == NAME

    camera_entity = camera._get_camera_from_entity_id(hass, entity_id)
    assert camera_entity.image_source == "http://1.2.3.4:80/axis-cgi/jpg/image.cgi"
    assert camera_entity.mjpeg_source == "http://1.2.3.4:80/axis-cgi/mjpg/video.cgi"
    assert (
        await camera_entity.stream_source()
        == "rtsp://root:pass@1.2.3.4/axis-media/media.amp?videocodec=h264"
    )


@pytest.mark.config_entry_options({CONF_STREAM_PROFILE: "profile_1"})
async def test_camera_with_stream_profile(hass, config_entry):
    """Test that Axis camera entity is using the correct path with stream profike."""
    await setup_axis_integration(hass, config_entry)

    assert len(hass.states.async_entity_ids(CAMERA_DOMAIN)) == 1

    entity_id = f"{CAMERA_DOMAIN}.{NAME}"

    cam = hass.states.get(entity_id)
    assert cam.state == STATE_IDLE
    assert cam.name == NAME

    camera_entity = camera._get_camera_from_entity_id(hass, entity_id)
    assert camera_entity.image_source == "http://1.2.3.4:80/axis-cgi/jpg/image.cgi"
    assert (
        camera_entity.mjpeg_source
        == "http://1.2.3.4:80/axis-cgi/mjpg/video.cgi?streamprofile=profile_1"
    )
    assert (
        await camera_entity.stream_source()
        == "rtsp://root:pass@1.2.3.4/axis-media/media.amp?videocodec=h264&streamprofile=profile_1"
    )


async def test_camera_disabled(hass, config_entry):
    """Test that Axis camera platform is loaded properly but does not create camera entity."""
    with patch("axis.vapix.vapix.Params.image_format", new=None):
        await setup_axis_integration(hass, config_entry)

    assert len(hass.states.async_entity_ids(CAMERA_DOMAIN)) == 0
