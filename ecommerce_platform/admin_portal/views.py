from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import *
from django.shortcuts import get_object_or_404
from cart_orders.models import Order
from cart_orders.serializers import OrderSerializer
from cart_orders.tasks import clear_xpressbees_token
from rest_framework.viewsets import ModelViewSet

# View for Admin Logs
class AdminLogView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = AdminLog.objects.all().order_by('-timestamp')
        serializer = AdminLogSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# View for Vendor Payouts
class VendorPayoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payouts = VendorPayout.objects.all().order_by('-created_at')
        serializer = VendorPayoutSerializer(payouts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, payout_id):
        payout = get_object_or_404(VendorPayout, id=payout_id)
        serializer = VendorPayoutSerializer(payout, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from authusers.models import VendorProfile
from .serializers import VendorProfileDetailSerializer

class VendorProfileDetailView(RetrieveAPIView):
    queryset = VendorProfile.objects.all()
    serializer_class = VendorProfileDetailSerializer
    permission_classes = [AllowAny]  # Restrict access to authenticated users
    lookup_field = 'id'  # This enables looking up the profile by its `id`



from rest_framework.generics import RetrieveUpdateAPIView


class VendorProfileUpdateView(RetrieveUpdateAPIView):
    queryset = VendorProfile.objects.all()
    serializer_class = VendorProfileUpdateSerializer
    permission_classes = [AllowAny]  # Ensure only authenticated users can access
    lookup_field = 'id' 



class RefundDetailView(APIView):
    """
    View and update refund details by order ID.
    """
    def get(self, request, order_id):
        try:
            refund = Refund.objects.get(order_item__id=order_id)
            serializer = RefundDetailSerializer(refund)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Refund.DoesNotExist:
            return Response({"error": "Refund not found for the provided order ID."}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, order_id):
        try:
            refund = Refund.objects.get(order_item__id=order_id)
            serializer = RefundUpdateSerializer(refund, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Refund status updated successfully."}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Refund.DoesNotExist:
            return Response({"error": "Refund not found for the provided order ID."}, status=status.HTTP_404_NOT_FOUND)



class RefundActionView(APIView):
    """
    A view to handle refund actions: processed, rejected, implemented.
    """
    permission_classes = [AllowAny]
    def post(self, request, refund_id, action):
        try:
            refund = Refund.objects.get(id=refund_id)
        except Refund.DoesNotExist:
            return Response({"error": "Refund not found"}, status=status.HTTP_404_NOT_FOUND)

        # Validate and update based on the action
        if action == "processed":
            if refund.status != "in_transmit":
                return Response({"error": "Refund must be in 'initiated' state to process."},
                                status=status.HTTP_400_BAD_REQUEST)
            refund.status = "processed"
            refund.refund_processed_date = now()

        elif action == "rejected":
            if refund.status not in ["requested", "in_transmit"]:
                return Response({"error": "Refund must be in 'initiated' or 'processed' state to reject."},
                                status=status.HTTP_400_BAD_REQUEST)
            refund.status = "rejected"
            refund.refund_rejected_date = now()

        elif action == "approved":
            if refund.status != "requested":
                return Response({"error": "Refund must be in 'processed' state to implement."},
                                status=status.HTTP_400_BAD_REQUEST)
            refund.status = "approved"
            refund.refund_implemented_date = now()

        else:
            return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

        # Save changes and respond
        refund.save()
        return Response({"message": f"Refund {action} successfully."}, status=status.HTTP_200_OK)
    

class ListPlacedOrdersView(APIView):
    """
    API View to list all orders with order_status = "placed".
    """
    permission_classes = [AllowAny]  # Only authenticated users can access

    def get(self, request):
        # Filter orders with order_status = "placed"
        placed_orders = Order.objects.filter(order_status="placed").order_by("-created_at")

        # Serialize the data
        serializer = OrderSerializer(placed_orders, many=True)

        # Return the serialized data as a response
        return Response(serializer.data, status=status.HTTP_200_OK)



class CreateSoftDataView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = SoftDataSerializer(data=request.data)
        if serializer.is_valid():
            soft_data = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# XPRESS_BEES LOGIN

import requests
from django.core.cache import cache 


class XpressBeeLogin(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        url = 'https://shipment.xpressbees.com/api/users/login'
        response = requests.post(url, json = request.data)

        try :
            if response.status_code == 200:
                res = response.json()
                cache.set("XPRESS_BEE", res.get("data"), timeout = 6*3600)
                

                return Response(response.json(), status = status.HTTP_200_OK)
        
        except:
            
            return Response("Invalied url", status = status.HTTP_200_OK)




class WareHouseAddressViewSet(ModelViewSet):
    """
    A viewset to handle CRUD operations for WareHouseAddress.
    """
    queryset = WareHouseAddress.objects.all()
    serializer_class = WareHouseAddressSerializer





class CreateReturnShipment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refund_id = request.data.get("refund_id")
        if not refund_id:
            return Response({"error": "Refund ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the refund and its associated order item
        try:
            refund = Refund.objects.get(id=refund_id, status="requested")
            order_item = refund.order_item  # Refund is linked to a single OrderItem
            order = order_item.order  # Get the associated Order
        except Refund.DoesNotExist:
            return Response({"error": "Valid refund request not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the order has an address (customer's pickup address)
        if not order.address:
            return Response({"error": "Order address not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch default warehouse (consignee/delivery address)
        warehouse = WareHouseAddress.objects.filter(is_default=True).first()
        if not warehouse:
            return Response({"error": "Default warehouse not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare the order item payload (single item return)
        order_item_payload = {
            "name": order_item.product_variant.product.name,
            "qty": order_item.quantity,
            "price": str(order_item.price),
            "sku": "555555",  # SKU placeholder (use actual SKU if available)
        }

        # Build payload for return shipment
        payload = {
            "order_number": f"#{order.id}-RET",
            "payment_type": "reverse",
            "package_weight": order_item.package_weight,
            "package_length": order_item.package_length,
            "package_breadth": order_item.package_breadth,
            "package_height": order_item.package_height,
            "request_auto_pickup": "yes",

            # Pickup from customer's address (where the product is being returned from)
            "pickup": {
                "name": order.address.full_name,
                "address": order.address.address_line_1,
                "address_2": order.address.address_line_2,
                "city": order.address.city,
                "state": order.address.state,
                "pincode": order.address.postal_code,
                "phone": order.address.phone_number,
            },

            # Deliver to warehouse (where the returned product is being sent)
            "consignee": {
                "warehouse_name": "Default Warehouse",
                "name": warehouse.full_name,
                "address": warehouse.address_line_1,
                "city": warehouse.city,
                "state": warehouse.state,
                "pincode": warehouse.postal_code,
                "phone": warehouse.phone_number,
            },

            "order_items": [order_item_payload],  # Single order item for return
            "courier_id": 1,
            "collectable_amount": 0,  # No amount collected for return
        }

        # Get Xpressbees token
        token = cache.get("XPRESS_BEE")
        if not token:
            return Response({"error": "Xpressbees login expired"}, status=status.HTTP_401_UNAUTHORIZED)

        # Send request to Xpressbees API
        url = "https://shipment.xpressbees.com/api/shipments2"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                response_data = response.json()
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Failed to create return shipment", "details": response.json()}, status=response.status_code)
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class CreateXpressBeeShipment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(request.data)
        print(Order.objects.filter(id=80).exists())
        print(WareHouseAddress.objects.filter(is_default=True).exists())

        warehouse = WareHouseAddress.objects.get(id=1)  # Ensure the warehouse exists
        print(warehouse.postal_code)

        # Fetch the order instance
        try:
            order = Order.objects.get(id=request.data["order_id"])  # Fetch a single instance
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Assign the primary key of the order to the request data
        request.data["order"] = order.id

        serializer = XpressBeeShipmentSerializer(data=request.data)

        print(serializer.is_valid())
        print(serializer.errors)
        
        token = cache.get("XPRESS_BEE")
        
        if not token:
            return Response(" Xpress Bees Login Expired",   status=status.HTTP_401_UNAUTHORIZED)
        if serializer.is_valid():
            shipment = serializer.save()
            order_items_payload = [
                {
                    "name": item.product_variant.product.name,
                    "qty": item.quantity,
                    "price": str(item.price),  # Convert Decimal to string
                    "sku": 555555  # Assuming the `ProductVariant` model has an SKU field
                }
                for item in order.items.all()
            ]
            # Build payload for Xpressbees API (rest of the logic remains unchanged)
            payload = {
                "order_number": f"#{shipment.order.id}",
                "shipping_charges": float(shipment.shipping_charges),
                "discount": float(shipment.discount),
                "cod_charges": float(shipment.cod_charges),
                "payment_type": shipment.payment_type,
                "order_amount": float(shipment.order_amount),
                "package_weight": shipment.package_weight,
                "package_length": shipment.package_length,
                "package_breadth": shipment.package_breadth,
                "package_height": shipment.package_height,
                "request_auto_pickup": "yes",
                "consignee": {
                    "name": shipment.order.address.full_name,
                    "address": shipment.order.address.address_line_1,
                    "address_2": shipment.order.address.address_line_2,
                    "city": shipment.order.address.city,
                    "state": shipment.order.address.state,
                    "pincode": 500061,
                    "phone": shipment.order.address.phone_number,
                },
                "pickup": {
                    "warehouse_name": "Default Warehouse",
                    "name": warehouse.full_name,
                    "address": warehouse.address_line_1,
                    "city": warehouse.city,
                    "state": warehouse.state,
                    "pincode": warehouse.postal_code,
                    "phone": warehouse.phone_number,
                },
                "order_items": order_items_payload,
                "courier_id": 1,
                "collectable_amount": float(shipment.collectable_amount),
            }
            


            # Send the payload to Xpressbees API
            url = "https://shipment.xpressbees.com/api/shipments2"
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
            try:
                response = requests.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    response_data = response.json()
                    shipment.xpressbees_awb_number = response_data.get("awb_number")
                    shipment.status = "booked"
                    shipment.save()
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {"error": "Failed to create shipment", "details": response.json()},
                        status=response.status_code,
                    )
            except requests.RequestException as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class TrackXpressBeeShipment(APIView):
    def post(self, request):
        token = cache.get("XPRESS_BEE")
        
        if not token:
            return Response(" Xpress Bees Login Expired",   status=status.HTTP_401_UNAUTHORIZED)

        awb_number = request.data["awb_number"] 
        headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                
            }

        try :
            url = f"https://shipment.xpressbees.com/api/shipments2/track/{awb_number}"
            response = requests.get(url, headers = headers )
            if response.status_code == 200:

                response_data = response.json()
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Failed to track shipment", "details": response.json()},
                    status=response.status_code,
                )
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerateManifestXpressBee(APIView):
    def post(self, request):
        token = cache.get("XPRESS_BEE")

        if not token:
            return Response({"error": "Xpress Bees Login Expired"}, status=status.HTTP_401_UNAUTHORIZED)

        awbs = request.data.get("awbs", [])
        if not awbs:
            return Response({"error": "AWBs list is required"}, status=status.HTTP_400_BAD_REQUEST)

        url = "https://shipment.xpressbees.com/api/shipments2/manifest"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        payload = {"awbs": awbs}  # Correct payload format

        try:
            response = requests.post(url, headers=headers, json=payload)  # Pass json=payload

            if response.status_code == 200:
                return Response(response.json(), status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Failed to generate manifest", "details": response.json()},
                    status=response.status_code,
                )
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CancelShipmentXpressBee(APIView):
    def post(self, request):
        token = cache.get("XPRESS_BEE")

        if not token:
            return Response({"error": "Xpress Bees Login Expired"}, status=status.HTTP_401_UNAUTHORIZED)

        awb = request.data.get("awb")
        if not awb:
            return Response({"error": "AWB is required"}, status=status.HTTP_400_BAD_REQUEST)

        url = "https://shipment.xpressbees.com/api/shipments2/cancel"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        payload = {"awb": awb}  # Correct payload format

        try:
            response = requests.post(url, headers=headers, json=payload)  # Pass json=payload

            if response.status_code == 200:
                return Response(response.json(), status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Failed to cancel shipment", "details": response.json()},
                    status=response.status_code,
                )
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




import hmac
import hashlib
import base64
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from ecommerce_platform.settings import XPRESSBEES_WEBHOOK_SECRET


class XpressBeesWebhook(APIView):
    """
    Webhook to handle shipment status updates from Xpressbees.
    """

    def get(self, request):
        """Used to test if webhook is reachable."""
        return Response({"message": "Webhook received"}, status=status.HTTP_200_OK)

    def verify_signature(self, request):
        """Verify the Xpressbees webhook signature"""
        received_signature = request.headers.get("X-Hmac-SHA256")
        payload = request.body  # Raw request body

        if not received_signature:
            return False  # Signature is missing

        # Generate HMAC SHA256 signature
        expected_signature = base64.b64encode(
            hmac.new(
                bytes(XPRESSBEES_WEBHOOK_SECRET, "utf-8"),  # Secret Key
                msg=payload,  # Webhook data
                digestmod=hashlib.sha256,
            ).digest()
        ).decode("utf-8")

        # Compare signatures
        return hmac.compare_digest(received_signature, expected_signature)

    @method_decorator(csrf_exempt)  # Disables CSRF for this endpoint
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        """
        Handle shipment status updates.
        """
        if not self.verify_signature(request):
            return JsonResponse({"error": "Invalid webhook signature"}, status=400)

        try:
            data = json.loads(request.body)  # Parse JSON request body
            awb_number = data.get("awb_number")
            shipment_status = data.get("status")

            if not awb_number or not shipment_status:
                return JsonResponse({"error": "AWB number and status are required"}, status=400)

            # Fetch shipment & related order
            shipment = get_object_or_404(XpressBeeShipment, xpressbees_awb_number=awb_number)
            order = shipment.order

            # Update order status based on shipment type
            if shipment.payment_type == "reverse":
                if shipment_status == "delivered":
                    order.order_status = "returned"
            else:
                if shipment_status == "in_transit":
                    order.order_status = "shipped"
                elif shipment_status == "delivered":
                    order.order_status = "delivered"

            order.save()
            return JsonResponse({"message": "Order status updated"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)



