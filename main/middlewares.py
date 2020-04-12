from .models import Basket

def basket_middleware(get_response):
    """Checks the session to see if a basket exists for every view request"""
    def middleware(request):
        if 'basket_id' in request.session:
            basket_id = request.session['basket_id']
            basket = Basket.objects.get(id=basket_id)
            request.basket = basket
        else:
            request.basket = None
        
        # Use the in-built get_response() function to pass the request along after adding the basket
        response = get_response(request) 
        return response
    return middleware
