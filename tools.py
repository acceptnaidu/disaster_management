import schedule
import time
import random
from datetime import datetime

def run_disaster_alerts(duration_seconds=120, interval_seconds=10):
    """
    Starts a simulated disaster alert system that triggers random alerts 
    every few seconds and stops after a given duration.
    
    Args:
        duration_seconds (int): Total runtime in seconds before auto-stop.
        interval_seconds (int): Frequency (in seconds) between alerts.
    """
    disasters = [
        "🌪️ Tornado Warning",
        "🔥 Wildfire Alert",
        "🌊 Tsunami Warning",
        "🌩️ Severe Thunderstorm",
        "🌧️ Flash Flood Watch",
        "❄️ Blizzard Conditions",
        "🦠 Biological Hazard Alert",
        "☢️ Nuclear Plant Leak",
        "💥 Earthquake Detected",
        "🌀 Hurricane Advisory"
    ]
    
    start_time = time.time()
    
    def check_disaster_conditions():
        current_time = time.time()
        if current_time - start_time > duration_seconds:
            print("\n✅ Time's up! Stopping disaster alerts.")
            schedule.clear()  # Stop further scheduling
            return
        
        alert = random.choice(disasters)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚨 ALERT: {alert}")
    
    print(f"🛡️ Disaster Alert Agent Started — Running for {duration_seconds} seconds...\n")
    schedule.every(interval_seconds).seconds.do(check_disaster_conditions)
    
    while schedule.jobs:
        schedule.run_pending()
        time.sleep(1)
