from django.core.paginator import Paginator, EmptyPage

def pagination(request,objects,nppage):
    ret = None
    paginator = Paginator(objects,nppage)
    try:
        page = request.GET.get('page')
        ret = paginator.page(page)
    except EmptyPage:
        ret = paginator.page(paginator.num_pages)
    except:
        ret = paginator.page(1)
    
    return ret