from django.contrib import admin
from .models import Tour, TourDestination, FoodPlan, TourBooking

class TourDestinationInline(admin.TabularInline):
    model = TourDestination
    extra = 1

class FoodPlanInline(admin.TabularInline):
    model = FoodPlan
    extra = 3

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('tour_id', 'tour_name', 'guide_group', 'total_seats', 'available_seats', 'price_per_person', 'status')
    list_filter = ('status', 'guide_group')
    search_fields = ('tour_name', 'description')
    inlines = [TourDestinationInline]

@admin.register(TourDestination)
class TourDestinationAdmin(admin.ModelAdmin):
    list_display = ('tour', 'destination', 'order', 'arrival_date', 'departure_date')
    inlines = [FoodPlanInline]

@admin.register(TourBooking)
class TourBookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'tour', 'traveller', 'number_of_travellers', 'total_amount', 'status', 'booking_date')
    list_filter = ('status', 'booking_date')
    search_fields = ('traveller__username', 'tour__tour_name')