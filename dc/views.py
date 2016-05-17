import docker
import json

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from .models import Node

@login_required
def index(request):
	context = {'nodes': request.user.node_set.all()}
	return render(request, 'dc/pages/dashboard.html', context)
	
def register(request):
	script = '''
	#!/bin/sh
	docker_id=$(docker run -d -p 2376 --privileged peragro/dc-agent)
	while ! docker logs $docker_id 2>&1 | grep "API listen" ; do sleep 10; done
	docker_port=$(docker inspect --format='{{(index (index .NetworkSettings.Ports "2376/tcp") 0).HostPort}}' $docker_id)
	curl -Ls http://192.168.1.3:8000/nodes/$1/register/ | docker exec -i $docker_id sign | curl -H "Content-Type: text/plain; charset=UTF-8" -H "X-Agent-port: $docker_port" -d @- http://192.168.1.3:8000/nodes/$1/register/
	'''

	return HttpResponse(script, content_type='application/json')
    
@login_required
def nodes(request):
	context = {'nodes': request.user.node_set.all()}
	return render(request, 'dc/pages/nodes.html', context)
	
@login_required
def node(request, node_uuid):
	node = get_object_or_404(Node, uuid=node_uuid)
	
	client = node.docker()
	
	containers = client.containers(all=True)
	
	context = {'node': node, 'info': client.info(), 'containers': containers}
	print containers
	return render(request, 'dc/pages/node.html', context)
	
@login_required
def add_node(request):
	new_nodes = Node.objects.filter(user=request.user, cert='')
	
	if len(new_nodes) < 1:
		node = Node(user=request.user)
		node.generate_key()
		node.save()
	else:
		node = new_nodes[0]
	
	jsondata = {'uuid': str(node.uuid), 'command': 'curl -Ls http://192.168.1.3:8000/register | sh -s '+str(node.uuid)}	

	return HttpResponse(json.dumps(jsondata), content_type='application/json')
	
@require_http_methods(["GET", "POST"])
@csrf_exempt
def register_node(request, node_uuid):
	#TODO Check expired
	node = get_object_or_404(Node, uuid=node_uuid)
	
	#REMOTE_ADDR
	if request.method == 'GET':
		certRequest = node.createCertRequest()
		return HttpResponse(certRequest, content_type='text/html')
	elif request.method == 'POST':
		ip =  request.META['REMOTE_ADDR']
		port = request.META['HTTP_X_AGENT_PORT']
		node.set_cert(request.read())
		node.address = 'https://'+ip+':'+port
		node.save()
		jsondata = {'status': 'ok', 'address': node.address}	
		return HttpResponse(json.dumps(jsondata), content_type='application/json')
	else:
		return HttpResponse('', status=400)

	