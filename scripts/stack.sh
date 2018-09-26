#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
set -o errtrace

cleanup() {
    echo "Quitting..."
    kill -- -$$ 2> /dev/null
}

trap cleanup EXIT
root="$(pwd)"
LOGLEVEL="${LOGLEVEL:-info}"

color_db='1 0'
color_api='6 0'
color_web='2 0'

tryget() {
    curl -sfL -q --max-time 1 "${@}" > /dev/null
}

color() {
    if [ -t 1 -a "$(tput colors)" -ge 8 ]; then
        case "${1}" in
        reset)
            tput sgr0;;
        *)
            tput setaf "${1}"

            if [ -n "${2:-}" ]; then
                tput setab "${2}"
            fi

            if [ -n "${3:-}" ]; then
                for f in ${3}; do
                    case "${f}" in
                    bold)
                        tput bold;;
                    blink)
                        tput blink;;
                    invert|rev)
                        tput rev;;
                    esac
                done
            fi
            ;;
        esac
    fi
}

while true; do
    echo "Starting Pivot (database abstraction layer)"
    cd "${root}/database"

    pivot -s schema -L "${LOGLEVEL}" -Q web 2>&1 | while read; do
        if [ -n "${REPLY}" ]; then
                echo -n "       "
                color $color_db
                echo -n "[db]"
                color reset
                echo "  ${REPLY}" 1>&2
        fi
    done

    sleep 1s
done &

while true; do
    if tryget 'http://localhost:29029/api/status'; then
        echo "Starting Python Backend (API layer)"

        export AWS_PROFILE=bop
        export SENTRY_DSN="https://c8fb63f1567f4ea9ac1e4e5c660f0412:32cdbb2eb62343a28bbe82ab9bb4c5ce@sentry.io/1283609"

        cd "${root}/backend"

        make debug 2>&1 | while read; do
            if [ -n "${REPLY}" ]; then
                echo -n "      "
                color $color_api
                echo -n "[api]"
                color reset
                echo "  ${REPLY}" 1>&2
            fi
        done
    fi

    sleep 1s
done &

while true; do
    if tryget 'http://localhost:5000/api/routes'; then
        echo "Starting Diecast (frontend templating engine)"
        cd "${root}/frontend"

        diecast -a :28419 -L "${LOGLEVEL}" 2>&1 | while read; do
            if [ -n "${REPLY}" ]; then
                echo -n "      "
                color $color_web
                echo -n "[web]"
                color reset
                echo "  ${REPLY}" 1>&2
            fi
        done
    fi

    sleep 1s
done &

while true; do
    if tryget 'http://localhost:29029/api/status'; then
        if tryget 'http://localhost:5000/api/routes'; then
            if tryget 'http://localhost:28419/api/routes'; then
                sleep 0.25s

                echo
                color 7 2 bold blink
                echo -n "READY"
                color reset
                echo

                echo "Local ${PIVOT_ENV} environment is running."
                echo -n "Go to "

                color 7 4
                echo -n "http://localhost:28419"
                color reset

                echo " to start using it!"
                echo
                break
            fi
        fi
    fi

    sleep 1s
done &

wait