#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail
set -o errtrace

cleanup() {
    echo "Quitting..."

    if [ -e log.fifo ]; then
        rm log.fifo
    fi

    kill -- -$$ 2> /dev/null
}

function os() {
    case "$(uname -s)" in
    Darwin)
        echo 'darwin';;
    Linux)
        echo 'linux';;
    FreeBSD)
        echo 'freebsd';;
    *)
        echo 'unknown';;
    esac
}

trap cleanup EXIT
root="$(pwd)"
LOGLEVEL="${LOGLEVEL:-info}"

color_dal='1 0'
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

if [ -e log.fifo ]; then
    rm log.fifo
fi

mkfifo log.fifo

while true; do
    if read; then
        c='reset'

        case "${REPLY}" in
        dal:*)
            c=$color_dal;;
        api:*)
            c=$color_api;;
        web:*)
            c=$color_web;;
        esac

        if [ -n "${REPLY}" ]; then

            if [ "${c}" != "reset" ]; then
                tag="${REPLY%%:*}"
                msg="${REPLY#*:}"

                echo -n "    "
                color $c
                echo -n "[${tag}]"
                color reset
                echo "  ${msg}" 1>&2
            else
                echo "${REPLY}" 1>&2
            fi
        fi
    fi
done < log.fifo &

while true; do
    echo "Starting Pivot (database abstraction layer)"
    cd "${root}/database"

    ../bin/$(os)/pivot -s schema -L "${LOGLEVEL}" -Q web 2>&1 | while read; do
        echo "dal:${REPLY}"
    done

    sleep 1s
done >> log.fifo 2>&1 &

while true; do
    if tryget 'http://localhost:29029/api/status'; then
        echo "Starting Python Backend (API layer)"

        export AWS_PROFILE=bop
        export SENTRY_DSN="https://c8fb63f1567f4ea9ac1e4e5c660f0412:32cdbb2eb62343a28bbe82ab9bb4c5ce@sentry.io/1283609"

        cd "${root}/backend"

        make debug 2>&1 | while read; do
            echo "api:${REPLY}"
        done
    fi

    sleep 1s
done >> log.fifo 2>&1 &

while true; do
    if tryget 'http://localhost:5000/api/routes'; then
        echo "Starting Diecast (frontend templating engine)"
        cd "${root}/frontend"

        ../bin/$(os)/diecast -a :28419 -L "${LOGLEVEL}" 2>&1 | while read; do
            echo "web:${REPLY}"
        done
    fi

    sleep 1s
done >> log.fifo 2>&1 &

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
done 2>&1 &

wait