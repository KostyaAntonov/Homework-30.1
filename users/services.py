import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_checkout(course_name: str, course_description: str, amount: float, success_url: str, cancel_url: str):
    """
    Создает продукт, цену и сессию оплаты в Stripe.
    Возвращает словарь с ID и ссылкой на оплату.
    """
    try:
        # 1. Создаем продукт в Stripe
        product = stripe.Product.create(
            name=course_name,
            description=course_description,
        )

        # 2. Создаем цену (amount умножаем на 100, так как Stripe принимает копейки/центы)
        price = stripe.Price.create(
            product=product.id,
            unit_amount=int(amount * 100),
            currency='rub',
        )

        # 3. Создаем сессию оплаты (Checkout Session)
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price.id,
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
        )

        return {
            'product_id': product.id,
            'price_id': price.id,
            'session_id': session.id,
            'payment_link': session.url,
        }
    except stripe.error.StripeError as e:
        # Пробрасываем ошибку дальше, чтобы обработать её во View
        raise Exception(f"Ошибка Stripe: {str(e)}")
