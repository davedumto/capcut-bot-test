import asyncio
import sys
import os
from pathlib import Path
import signal
import traceback
from datetime import datetime

# Add bot directory to path
sys.path.insert(0, str(Path(__file__).parent))

from bot import CapCutPasswordResetBot
import requests

class BotWorker:
    def __init__(self, backend_url="http://localhost:8000"):
        self.backend_url = backend_url
        self.is_running = True
        self.last_heartbeat = datetime.now()
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3
        
    def signal_handler(self, signum, frame):
        """Handle graceful shutdown"""
        print("\n🛑 Shutdown signal received, stopping worker...")
        self.is_running = False
        
    async def send_heartbeat(self):
        """Send heartbeat to backend to indicate worker is alive"""
        try:
            requests.post(
                f"{self.backend_url}/api/admin/bot-worker/heartbeat",
                json={
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "consecutive_failures": self.consecutive_failures
                },
                timeout=5
            )
            self.last_heartbeat = datetime.now()
        except Exception as e:
            print(f"⚠️  Failed to send heartbeat: {e}")
    
    async def run(self):
        """Main worker loop with health checks"""
        print("🤖 Bot Worker started - polling for jobs every 30s")
        print("💓 Heartbeat enabled - sending health status every 60s")
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        heartbeat_counter = 0
        
        while self.is_running:
            try:
                # Send heartbeat every 60 seconds (every 2 iterations)
                if heartbeat_counter % 2 == 0:
                    await self.send_heartbeat()
                
                # Process next job
                await self.process_next_job()
                
                # Reset consecutive failures on successful iteration
                if self.consecutive_failures > 0:
                    self.consecutive_failures = 0
                    
                heartbeat_counter += 1
                
            except Exception as e:
                self.consecutive_failures += 1
                print(f"❌ Error in worker loop: {e}")
                print(f"📊 Consecutive failures: {self.consecutive_failures}/{self.max_consecutive_failures}")
                traceback.print_exc()
                
                # Alert backend about critical failures
                if self.consecutive_failures >= self.max_consecutive_failures:
                    await self.alert_critical_failure()
                    print("⚠️  Max consecutive failures reached - continuing but alerting admin")
            
            await asyncio.sleep(30)
        
        print("✅ Worker stopped gracefully")
    
    async def alert_critical_failure(self):
        """Alert backend about critical worker failures"""
        try:
            requests.post(
                f"{self.backend_url}/api/admin/bot-worker/alert",
                json={
                    "type": "critical_failure",
                    "consecutive_failures": self.consecutive_failures,
                    "timestamp": datetime.now().isoformat()
                },
                timeout=5
            )
        except Exception as e:
            print(f"⚠️  Failed to send alert: {e}")
    
    async def process_next_job(self):
        """Process next job from queue"""
        # Get next pending job
        try:
            response = requests.get(f"{self.backend_url}/api/bot-jobs/next", timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Failed to fetch next job: {e}")
            return
        
        if not data.get("job"):
            print("⏸️  No pending jobs")
            return
        
        job = data["job"]
        job_id = job["id"]
        
        print(f"📋 Processing job {job_id} for session {job['session_id']}")
        
        # Mark as processing
        try:
            requests.patch(
                f"{self.backend_url}/api/bot-jobs/{job_id}/status",
                json={"status": "processing"},
                timeout=10
            )
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Failed to update job status: {e}")
            return
        
        try:
            # Run password reset bot
            bot = CapCutPasswordResetBot(
                capcut_email=job["capcut_email"],
                gmail_email=job["gmail_email"],
                gmail_app_password=job["gmail_app_password"],
                headless=True
            )
            
            success, new_password = await bot.run_complete_flow()
            
            if success:
                # Complete job and send credentials
                requests.post(
                    f"{self.backend_url}/api/bot-jobs/{job_id}/complete",
                    json={"new_password": new_password},
                    timeout=10
                )
                print(f"✅ Job {job_id} completed successfully")
            else:
                # Mark as failed
                requests.patch(
                    f"{self.backend_url}/api/bot-jobs/{job_id}/status",
                    json={"status": "failed", "error_message": "Bot failed to reset password"},
                    timeout=10
                )
                print(f"❌ Job {job_id} failed")
                
        except Exception as e:
            # Mark as failed with error
            error_trace = traceback.format_exc()
            try:
                requests.patch(
                    f"{self.backend_url}/api/bot-jobs/{job_id}/status",
                    json={
                        "status": "failed", 
                        "error_message": f"{str(e)[:200]}..."  # Truncate long errors
                    }, 
                    timeout=10
                )
            except:
                pass
            
            print(f"❌ Job {job_id} error: {e}")
            print(f"Stack trace:\n{error_trace}")

if __name__ == "__main__":
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    print("=" * 60)
    print("🚀 CapCut Bot Worker v2.0")
    print("=" * 60)
    print(f"Backend URL: {backend_url}")
    print(f"Health checks: ENABLED")
    print(f"Auto-restart: ENABLED (via supervisor/systemd)")
    print("=" * 60)
    
    while True:
        try:
            worker = BotWorker(backend_url)
            asyncio.run(worker.run())
            print("🔄 Worker exited, restarting in 5 seconds...")
            asyncio.run(asyncio.sleep(5))
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"💥 Worker crashed: {e}")
            print("🔄 Auto-restarting in 10 seconds...")
            asyncio.run(asyncio.sleep(10))
