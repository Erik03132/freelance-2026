#!/bin/bash

# Hermes Skills Sync Daemon
# Main synchronization daemon for Hermes Skills

# Load configuration
CONFIG_FILE="/Users/igorvasin/freelance-2026/hermes-skills-sync/config.yaml"

# Default configuration values
CANON_DIR="/Users/igorvasin/freelance-2026/hermes-skills-sync/skills"
RUNTIME_DIR="/Users/igorvasin/.hermes/profiles"
VPS_HOST="user@vps-217-149-23-113"
LOG_DIR="/Users/igorvasin/freelance-2026/hermes-skills-sync/logs"
SYNC_INTERVAL="18000"
MAX_RETRIES="3"

# Parse config file if it exists
if [ -f "$CONFIG_FILE" ]; then
    # Simple config parsing (for demonstration)
    if grep -q "canon_dir:" "$CONFIG_FILE"; then
        CANON_DIR=$(grep "canon_dir:" "$CONFIG_FILE" | awk '{print $2}' | tr -d '"')
    fi
    if grep -q "runtime_dir:" "$CONFIG_FILE"; then
        RUNTIME_DIR=$(grep "runtime_dir:" "$CONFIG_FILE" | awk '{print $2}' | tr -d '"')
    fi
    if grep -q "vps_host:" "$CONFIG_FILE"; then
        VPS_HOST=$(grep "vps_host:" "$CONFIG_FILE" | awk '{print $2}' | tr -d '"')
    fi
    if grep -q "log_dir:" "$CONFIG_FILE"; then
        LOG_DIR=$(grep "log_dir:" "$CONFIG_FILE" | awk '{print $2}' | tr -d '"')
    fi
fi

# Logging function
log() {
    local level="$1"
    local message="$2"
    local timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_DIR/daemon.log"
}

# Function to sync from canon to runtime
sync_canon_to_runtime() {
    local agent="$1"
    local canon_path="$CANON_DIR/$agent"
    local runtime_path="$RUNTIME_DIR/$agent/skills/$agent"
    
    if [ ! -d "$canon_path" ]; then
        log "WARN" "Canon directory $agent not found"
        return 1
    fi
    
    # Create runtime directory structure
    mkdir -p "$(dirname "$runtime_path")"
    
    # Sync with rsync for efficiency
    if command -v rsync >/dev/null 2>&1; then
        rsync -av --delete "$canon_path/" "$runtime_path/" >> "$LOG_DIR/daemon.log" 2>&1
    else
        log "ERROR" "rsync command not found"
        return 1
    fi
    
    if [ $? -eq 0 ]; then
        log "INFO" "Sync completed: $agent → runtime"
    else
        log "ERROR" "Sync failed: $agent"
    fi
}

# Function to sync from canon to VPS
sync_canon_to_vps() {
    local agent="$1"
    local canon_path="$CANON_DIR/$agent"
    
    if [ ! -d "$canon_path" ]; then
        log "WARN" "Canon directory $agent not found"
        return 1
    fi
    
    # Sync to VPS using SSH
    if command -v ssh >/dev/null 2>&1 && command -v rsync >/dev/null 2>&1; then
        rsync -av --delete --partial --progress "$canon_path/" "$VPS_HOST:/home/user/freelance-2026/skills/$agent/" >> "$LOG_DIR/daemon.log" 2>&1
    else
        log "ERROR" "ssh or rsync command not found"
        return 1
    fi
    
    if [ $? -eq 0 ]; then
        log "INFO" "VPS sync completed: $agent"
    else
        log "ERROR" "VPS sync failed: $agent"
    fi
}

# Function to validate runtime profiles
validate_runtime_profiles() {
    log "INFO" "Validating runtime profiles"
    
    for profile_dir in "$RUNTIME_DIR"/*/; do
        local profile_name=$(basename "$profile_dir")
        local skills_dir="$profile_dir/skills"
        
        if [ -d "$skills_dir" ]; then
            for agent_dir in "$skills_dir"/*/; do
                local agent_name=$(basename "$agent_dir")
                
                # Check if canonical agent exists
                if [ ! -d "$CANON_DIR/$agent_name" ]; then
                    log "WARN" "Canon agent $agent_name not found for profile $profile_name"
                fi
                
                # Check for broken symlinks
                find "$agent_dir" -type l -exec test ! -e "{}" \; -print | while read -r broken_link; do
                    log "ERROR" "Broken symlink in $profile_name: $broken_link"
                done
            done
        fi
    done
}

# Main sync function
sync_all() {
    log "INFO" "Starting sync cycle"
    
    # Sync canon to runtime
    for agent_dir in "$CANON_DIR"/*/; do
        local agent_name=$(basename "$agent_dir")
        log "INFO" "Syncing $agent_name"
        
        sync_canon_to_runtime "$agent_name"
        sync_canon_to_vps "$agent_name"
    done
    
    # Validate runtime profiles
    validate_runtime_profiles
    
    log "INFO" "Sync cycle completed"
}

# Main execution
main() {
    log "INFO" "Starting Hermes Skills Sync Daemon"
    
    # Create logs directory
    mkdir -p "$LOG_DIR"
    
    # Main sync loop
    while true; do
        sync_all
        
        # Wait before next iteration
        sleep "$SYNC_INTERVAL"
    done
}

# Execute main function
main
