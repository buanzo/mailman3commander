#!/usr/bin/env bash
#
# Example: reconnect to the Mailman core container after ``setup.sh`` completes.
#
# The ``setup.sh`` script that initializes the Mailman 3 stack typically exits
# after bringing the containers up.  The services keep running in the
# background.  This helper script shows how an administrator can reconnect and
# run management commands again.

# List available mailing lists
# (equivalent to ``mailman lists`` inside the container)
docker compose exec -T mailman-core mailman lists

# Start the interactive Mailman3 Commander menu
# (requires ``mailman3commander`` to be installed inside the container)
docker compose exec -T mailman-core m3c
