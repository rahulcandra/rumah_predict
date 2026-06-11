# -----------------------------------------------------------------
#  run.py
#  Veltrix - Application entry point.
# -----------------------------------------------------------------

import os
from app import create_app

# Create the Flask application using the factory function
app = create_app()

if __name__ == "__main__":
    # Read host and port from environment variables (with sane defaults)
    host  = os.environ.get("FLASK_RUN_HOST", "127.0.0.1")
    port  = int(os.environ.get("FLASK_RUN_PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")

    print(f"\n  * Veltrix is running -> http://{host}:{port}\n")
    app.run(host=host, port=port, debug=debug)
