The script expects an API token in PINGDOM\_API\_TOKEN (override with --token-env).

example:

python pingdom\_checks.py pause "string1" "string2"

python pingdom\_checks.py resume "string1" "string2"



This script will pause or resume all checks that contain the strings passed as parameter using an OR logic. This script can be used through CI/CD pipeline to pause/resume Pingdom checks before after deployment during a maintenance window.



