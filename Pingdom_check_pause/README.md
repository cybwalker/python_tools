The script expects an API token in PINGDOM_API_TOKEN (override with --token-env).

example:
python pingdom_checks.py pause "string1" "string2"
python pingdom_checks.py resume "string1" "string2"

This script will pause or resume all checks that contain the strings passed as parameter using an OR logic. This script can be used through CI/CD pipeline to pause/resume Pingdom checks before after deployment during a maintenance window.