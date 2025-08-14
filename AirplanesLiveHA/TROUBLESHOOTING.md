# Troubleshooting Guide

This guide helps you resolve common issues with the Airplanes Live API Add-on.

## Common Issues and Solutions

### 1. No Aircraft Showing

**Symptoms**: Add-on is running but no aircraft entities appear in Home Assistant.

**Possible Causes**:
- Invalid coordinates
- Radius too small
- API endpoint issues
- No aircraft in your area

**Solutions**:
1. **Check coordinates**: Ensure latitude is between -90 and 90, longitude between -180 and 180
2. **Increase radius**: Try increasing the radius to 100-200 km
3. **Verify location**: Use a mapping service to confirm your coordinates
4. **Check logs**: Look for API errors in the add-on logs

**Example coordinates for testing**:
```yaml
# Major airport locations
latitude: 40.6413    # JFK Airport, New York
longitude: -73.7781
radius: 100
```

### 2. MQTT Connection Issues

**Symptoms**: Add-on starts but can't connect to MQTT broker.

**Possible Causes**:
- MQTT broker not running
- Incorrect broker address/port
- Authentication issues
- Network connectivity problems

**Solutions**:
1. **Verify MQTT broker**: Ensure Mosquitto add-on is installed and running
2. **Check credentials**: Verify username/password if authentication is enabled
3. **Test connection**: Try connecting with an MQTT client to verify broker accessibility
4. **Check logs**: Look for MQTT connection errors in add-on logs

**Common MQTT settings**:
```yaml
mqtt_broker: core-mosquitto  # Default Home Assistant MQTT broker
mqtt_port: 1883              # Default MQTT port
mqtt_username: ""            # Leave empty for no authentication
mqtt_password: ""            # Leave empty for no authentication
```

### 3. Configuration Validation Errors

**Symptoms**: Add-on fails to start with configuration errors.

**Possible Causes**:
- Invalid coordinate values
- Non-numeric values in numeric fields
- Values outside acceptable ranges

**Solutions**:
1. **Check data types**: Ensure all values are proper numbers
2. **Validate ranges**: 
   - Latitude: -90 to 90
   - Longitude: -180 to 180
   - Radius: > 0
   - Update interval: ≥ 1
3. **Restart add-on**: After fixing configuration, restart the add-on

**Valid configuration example**:
```yaml
latitude: 40.7128      # Valid latitude
longitude: -74.0060    # Valid longitude
radius: 50             # Valid radius
update_interval: 10    # Valid update interval
```

### 4. API Errors

**Symptoms**: Add-on logs show API connection failures or timeouts.

**Possible Causes**:
- Network connectivity issues
- API endpoint changes
- Rate limiting
- Firewall blocking

**Solutions**:
1. **Check network**: Ensure your Home Assistant instance can reach the internet
2. **Verify API endpoint**: Confirm the API URL is correct
3. **Increase timeout**: The add-on now uses 15-second timeout by default
4. **Check firewall**: Ensure outbound HTTPS connections are allowed

**API endpoint verification**:
```yaml
api_url: "https://api.airplanes.live/v2/point"  # Default endpoint
```

### 5. Individual Aircraft Not Appearing

**Symptoms**: Summary data works but individual aircraft entities don't show.

**Possible Causes**:
- Tracking mode set to "summary" only
- MQTT discovery issues
- Entity creation failures

**Solutions**:
1. **Check tracking mode**: Ensure it's set to "detailed" or "both"
2. **Verify MQTT topics**: Check that individual aircraft topics are being published
3. **Check logs**: Look for individual aircraft publishing errors
4. **Restart Home Assistant**: Sometimes MQTT discovery needs a restart

**Tracking mode options**:
```yaml
tracking_mode: summary    # Summary statistics only
tracking_mode: detailed   # Individual aircraft only
tracking_mode: both       # Both summary and detailed
```

### 6. Performance Issues

**Symptoms**: Add-on is slow, uses high CPU, or causes delays.

**Possible Causes**:
- Update interval too frequent
- Large radius causing many aircraft
- MQTT publishing overhead

**Solutions**:
1. **Increase update interval**: Try 15-30 seconds instead of 10
2. **Reduce radius**: Smaller radius means fewer aircraft to process
3. **Use summary mode**: If detailed tracking isn't needed, use summary mode only
4. **Monitor resources**: Check CPU and memory usage in Home Assistant

**Performance optimization example**:
```yaml
update_interval: 30    # Less frequent updates
radius: 25             # Smaller search area
tracking_mode: summary # Summary only for better performance
```

## Log Analysis

### Understanding Log Levels

- **INFO**: Normal operation messages
- **WARNING**: Non-critical issues that don't stop operation
- **ERROR**: Problems that affect functionality
- **CRITICAL**: Severe issues that prevent operation

### Common Log Messages

**Successful startup**:
```
[INFO] Starting Airplanes Live Home Assistant Add-on v1.4.0
[INFO] Configuration validation passed
[INFO] MQTT connection established successfully
[INFO] Discovery publishing completed
```

**Configuration errors**:
```
[ERROR] Configuration error: Latitude 95.0 is out of range (-90 to 90)
[CRITICAL] Configuration validation failed. Please check your settings.
```

**API issues**:
```
[ERROR] API request timed out
[ERROR] Failed to connect to API - network error
[WARNING] Unexpected API response format: <class 'str'>
```

**MQTT issues**:
```
[WARNING] MQTT connection failed - retrying...
[ERROR] MQTT authentication failed - check username/password
[CRITICAL] Failed to connect to MQTT broker after maximum retries
```

## Testing and Verification

### 1. Test API Endpoint

Test the API endpoint directly to verify it's working:

```bash
# Replace with your coordinates
curl "https://api.airplanes.live/v2/point/40.7128/-74.0060/50"
```

Expected response should contain an `ac` array with aircraft data.

### 2. Test MQTT Connection

Use an MQTT client to test connectivity:

```bash
# Install mosquitto-clients
mosquitto_sub -h core-mosquitto -t "airplanes/live/#" -v
```

### 3. Verify Entity Creation

Check that entities are created in Home Assistant:
1. Go to Settings > Devices & Services
2. Look for "Airplanes Live" device
3. Verify sensors are present and updating

## Getting Help

If you're still experiencing issues:

1. **Check the logs**: Look for specific error messages
2. **Verify configuration**: Use the example configuration as a reference
3. **Test with defaults**: Try the default configuration first
4. **Check GitHub**: Visit the [GitHub repository](https://github.com/BenCos17/airplanesliveHA) for issues and discussions
5. **Create an issue**: Include logs, configuration, and steps to reproduce

## Performance Tips

1. **Start simple**: Begin with summary mode and small radius
2. **Monitor resources**: Watch CPU and memory usage
3. **Adjust update frequency**: Balance between real-time data and performance
4. **Use appropriate tracking mode**: Choose based on your needs
5. **Regular restarts**: Restart the add-on periodically to clear any memory issues
