import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import os
import logging

logger = logging.getLogger(__name__)

def init_sentry() -> None:
    """
    Initialize Sentry only if DSN is available
    """
    sentry_dsn = os.getenv('SENTRY_DSN')
    
    if not sentry_dsn:
        print("Sentry: brak DSN, monitoring wylaczony")
        return
    
    environment = os.getenv("NODE_ENV", os.getenv("ENVIRONMENT", "development"))
    
    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=environment,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            StarletteIntegration(transaction_style="endpoint"),
            LoggingIntegration(
                level=logging.INFO,        
                event_level=logging.ERROR
            ),
        ],

        send_default_pii=True,

        traces_sample_rate=1.0,

    )
    
    print(f"Sentry: monitoring wlaczony (environment: {environment})")