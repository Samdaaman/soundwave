# Layout
### Soundwave - C2 centre
- Manages high level functions status, control and settings
- Serves the web server and ~~API~~ that Wheelie and Ravage connect to
- Inspired by the robot that hacks the satellite and spends time in orbit

### Wheelie - Initial file
- Lightweight and sets up further communication channels
- Inspired by the small pest-like robot

### Ravage - Larger file
- Serves as the main running file on the compromised system
- Is downloaded and run by wheelie
- Inspired by Soundwave's partner in crime that specialises in infiltration

---
# Soundwave Ports
- 1337 - Web server port
- 1338 - Initial hello (ping-back) port
- 1339 - Command channel to Ravage
- 13370+ - Reverse shell ports