kill -INT `cat /tmp/uwsgi.pid`
sleep 1
uwsgi --emperor --yaml app.yaml

