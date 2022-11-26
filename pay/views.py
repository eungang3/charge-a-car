import json 

from django.http      import JsonResponse
from django.views     import View
from django.conf      import settings

class Pay:
    def __init__(self, name, user_id, amount, actual_amount, coupon_id, card_id, pay_day):
        self.name = name  
        self.user_id = user_id
        self.amount = amount 
        self.actual_amount = actual_amount
        self.coupon_id = coupon_id
        self.card_id = card_id 
        self.pay_day = pay_day

    # 선불금충전, 바로결제
    def pay_now(self, name):
        pass 
    
    # 후불결제
    def pay_later(self):
        pass

    # 후불결제실행
    def pay_later_execute(self):
        pass 

    # 선불금사용
    def pay_with_balance(self):
        pass
    
class PayView(View):
    def post(self, request):
        data = json.loads(request.body)
        name = data.get('name')
        user_id = data.get('user_id')
        amount = data.get('amount')
        actual_amount = data.get('actual_amount')
        coupon_id = data.get('coupon_id')
        card_id = data.get('card_id')
        pay_day = data.get('pay_day')
        
        payment = Pay(name, user_id, amount, actual_amount, coupon_id, card_id, pay_day)

        if name == "선불금충전" :
            payment.pay_now("선불금충전") 

        elif name == "바로결제" :
            payment.pay_now("바로결제")  

        elif name == "후불결제" : 
            payment.pay_later() 

        elif name == "후불결제실행":
            payment.pay_later_execute()

        elif name == "선불금사용":
            payment.pay_with_balance()

        return JsonResponse({"message" : '유효하지 않은 name입니다.'}, status=401)
