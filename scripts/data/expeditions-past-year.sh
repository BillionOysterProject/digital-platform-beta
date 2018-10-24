curl -s -S -f -L 'http://localhost:28419/api/expeditions/?noexpand=true&fields=team,created&limit=false&q=created/gt:2017-10-17/status/published&sort=created' | jq -r '.[] | .team' | sort | uniq -c | while read count team; do
    curl -s -S -f -L "http://localhost:28419/api/teams/${team}" | jq -r "[ .name, .schoolOrg.name, (${count} | tostring), .schoolOrg.organizationType, .schoolOrg.schoolType, .schoolOrg.city ] | join(\"\t\")"
done