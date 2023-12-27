from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import subprocess
from django.views.decorators.http import require_POST
#from .chat import generate
from django.http import HttpResponse
from .gnn_model import generate_response

def index(request):
    iframe_urls = {
        'net1': 'figures/net1.html',
        'net2': 'figures/net2.html',
        'plot2': 'figures/plot2.html',
        'plot1': 'figures/plot1.png',
    }
        
    return render(request, 'index.html', {'iframe_urls': iframe_urls})

@csrf_exempt 
@require_POST
def generate(request):
    try:
        user_message = request.POST.get('user_message')

        question_text = f"{user_message}\n   answer briefly very short"
        output_compare_test = generate_response(question_text)
        print(output_compare_test)

        return JsonResponse({'output': output_compare_test})

    except Exception as e:
        return JsonResponse({'error': str(e)})
    
@csrf_exempt  # Use this decorator if you want to exempt CSRF protection for this view
def generate_graphs(request):
    if request.method == 'POST':
        try:
            subprocess.run(['python', 'mainApp/models/node_embeddings.py'])
            return HttpResponse('Done')
        except Exception as e:
            return HttpResponse(f'Error: {e}', status=500)
    else:
        return HttpResponse('Method not allowed', status=405)
