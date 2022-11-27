import json 
import requests
import uuid

from django.http import JsonResponse
from django.views import View
from django.conf import settings
from django.db import transaction

from users.models import User, Card 
from coupons.models import Coupon
from pay.models import Order, Payment

class Iamport:
    def __init__(self, config):
        self.api_key = config.api_key
        self.secret = config.secret

    def get_access_token(self):
        data = {
            'imp_key' : self.api_key,
            'imp_secret' : self.secret
        }
        headers = { 
            'Content-Type' : 'application/json' 
        }
        response = requests.post('https://api.iamport.kr/users/getToken', data=data, headers=headers).json()
        return response.get('acccess_token')

    def make_payment(self, access_token, customer_uid, merchant_uid, amount, name):
        headers = {
            'Authorization' : access_token
        }
        data = {
            'customer_uid' : customer_uid,
            'merchant_uid' : merchant_uid,
            'amount' : amount,
            'name' : name
        }
        # 모든 결제는 카드등록 후 이루어지므로 아임포트 정기결제 api 호출
        response = requests.post('https://api.iamport.kr/subscribe/payments/again', data=data, headers=headers).json()
        
        # 카드사 통신에 성공
        if response['code'] == 0:
            # 카드 정상 승인
            if response['status'] == 'paid':
                return response['imp_uid']

            # 카드 승인 실패(ex. 한도초과, 잔액부족 등)
            else:
                return False

        # 카드사 통신에 실패
        else:
            return False

    def get_paid_amount(self, access_token, imp_uid):
        headers = {
            'Authorization' : access_token
        }
        response = requests.get(f'https://api.iamport.kr/payments/${imp_uid}', headers=headers).json()
        return response.get('amount')

class Pay:
    def __init__(self, name, user_id, amount, actual_amount, coupon_id, card_id, pay_day):
        self.name = name  
        self.user_id = user_id
        self.amount = amount 
        self.actual_amount = actual_amount
        self.coupon_id = coupon_id
        self.card_id = card_id 
        self.pay_day = pay_day
        self.iamport = Iamport(settings.IAMPORT_CONFIG)

    # 선불금충전, 바로결제
    def pay_now(self):
        if not self.name or not self.user_id or not self.amount or not self.actual_amount or not self.card_id:
            return JsonResponse({"message":"필수값이 없습니다."}, status=401)

        order = Order.objects.create(
            status = 'pending', 
            user_id = self.user_id,
            amount = self.amount,
            actual_amount = self.actual_amount,
            name = self.name,
            coupon_id = self.coupon_id,
            card_id = self.card_id
            )

        merchant_uid = str(uuid.uuid4())

        payment = Payment.objects.create(
            merchant_uid = merchant_uid,
            status = 'ready',
            amount = self.actual_amount
        )

        customer_uid = Card.objects.get(id=self.card_id).customer_uid
        access_token = self.iamport.get_access_token()
        imp_uid = self.iamport.make_payment(access_token, customer_uid, merchant_uid, self.actual_amount, self.name)
        
        if not imp_uid:
            return JsonResponse({"message":"결제에 실패했습니다."}, status=401)

        paid_amount = self.iamport.get_paid_amount(self, access_token, imp_uid)

        if paid_amount == order.actual_amount:
            payment.imp_uid = imp_uid
            payment.status = 'paid'
            payment.save()
            order.payment_id = payment.id
            order.status = 'paid'
            order.save()
            return JsonResponse({"message":"결제 성공"}, status=201)
        else:
            return JsonResponse({"message":"결제 금액이 요청과 일치하지 않습니다."}, status=401)

    # 선불금사용
    def pay_with_balance(self):
        if not self.name or not self.user_id or not self.amount or not self.actual_amount:
            return JsonResponse({"message":"필수값이 없습니다."}, status=401)

        with transaction.atomic():
            user = User.objects.get(id=self.user_id)

            if self.actual_amount <= user.balance:
                user.balance -= self.actual_amount
                user.save()

                Order.objects.create(
                    status = 'paid', 
                    user_id = self.user_id,
                    amount = self.amount,
                    actual_amount = self.actual_amount,
                    name = self.name,
                    coupon_id = self.coupon_id
                    )

                return JsonResponse({"message" : "결제 성공"}, status=201)
            
            else: 
                return JsonResponse({"message" : "선불금이 부족합니다."}, status=401)

    # 후불결제
    def pay_later(self):
        if not self.name or not self.user_id or not self.amount or not self.actual_amount or not self.card_id:
            return JsonResponse({"message":"필수값이 없습니다."}, status=401)

        Order.objects.create(
            status = 'pending', 
            user_id = self.user_id,
            amount = self.amount,
            actual_amount = self.actual_amount,
            name = self.name,
            coupon_id = self.coupon_id,
            card_id = self.card_id
            )

        return JsonResponse({"message":"결제 예약 성공"}, status=201)

    # 후불결제실행
    def pay_later_execute(self):
        if not self.pay_day:
            return JsonResponse({"message":"필수값이 없습니다."}, status=401)
            
        pending_orders = Order.objects\
            .select_related('card')\
            .filter(status='pending', name='후불결제', card__pay_day=self.pay_day)
    
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
            payment.pay_now() 

        elif name == "바로결제" :
            payment.pay_now()  

        elif name == "후불결제" : 
            payment.pay_later() 

        elif name == "후불결제실행":
            payment.pay_later_execute()

        elif name == "선불금사용":
            payment.pay_with_balance()

        return JsonResponse({"message" : '유효하지 않은 name입니다.'}, status=401)
