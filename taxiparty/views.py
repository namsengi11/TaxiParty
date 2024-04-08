from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from .models import TaxiParty, Location
from .forms import TaxiPartyForm, LocationForm    

# Create your views here.
def createTaxiParty_view(request):
    if request.user.is_anonymous:
        return redirect(reverse('user:login'))
    form = TaxiPartyForm(request.POST or None)
    if form.is_valid():
        party = form.save()
        party.rider.add(request.user)
        party.owner = request.user
        print(party.owner)
        party.save()
        return redirect(reverse('taxiparty:taxipartydynamic', kwargs={"id": party.id}))
    
    context = {
        'form': form
    }
    return render(request, "createtaxiparty.html", context)

def create_location_view(request):
    if request.user.is_anonymous:
        return redirect(reverse('user:login'))
    form = LocationForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect(reverse('taxiparty:home'))
    
    context = {
        'form': form
    }
    return render(request, "create_location.html", context)

def home_view(request):
    partyList = TaxiParty.objects.all()
    
    context = {
        "partyList": partyList
    }
    return render(request, "taxipartyhome.html", context)

def view_location_view(request):
    locationList = Location.objects.all()
    
    context = {
        "locationList": locationList
    }
    return render(request, "view_location.html", context)

def dynamic_lookup_view(request, id):
    obj = get_object_or_404(TaxiParty, id=id)
    joinable = (request.user not in obj.rider.all())
    anon = request.user.is_anonymous
    context = {
        "party": obj,
        "joinable": joinable,
        "anon": anon
    }
    return render(request, "partydetail.html", context)

def party_edit_view(request, id):
    if request.user.is_anonymous:
        return redirect(reverse('user:login'))
    obj = get_object_or_404(TaxiParty, id=id)
    if request.user != obj.owner:
        messages.info(request, 'You are not the owner of the Taxi Party!')
        return redirect(reverse('taxiparty:taxipartydynamic', kwargs={'id': id}))
    if request.method == 'POST':    
        form = TaxiPartyForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect(reverse('taxiparty:taxipartydynamic', kwargs={'id': id}))
    else:
        form = TaxiPartyForm(instance=obj)
    context = {
        'form': form
    }
    return render(request, 'edit_party.html', context)

def party_join_view(request, id):
    if request.user.is_anonymous:
        return redirect(reverse('user:login'))
    joiner = request.user
    obj = get_object_or_404(TaxiParty, id=id)
    obj.rider.add(joiner)
    if obj.owner == None:
        obj.owner = joiner
    obj.save()
    return redirect(reverse('taxiparty:taxipartydynamic', kwargs={'id': id}))

def party_leave_view(request, id):
    if request.user.is_anonymous:
        return redirect(reverse('user:login'))
    obj = get_object_or_404(TaxiParty, id=id)
    riders = obj.rider.all()
    if request.user not in riders:
        messages.info(request, 'You are not part of the Taxi Party!')
        return redirect(reverse('taxiparty:taxipartydynamic', kwargs={'id': id}))
    else:
        leavingUser = request.user
        obj.rider.remove(leavingUser)
        riders = obj.rider.all()
        if obj.owner == leavingUser and len(obj.rider.all()) == 0:
            obj.owner = None
        elif obj.owner == leavingUser:
            obj.owner = riders[0]
        obj.save()
        return redirect(reverse('taxiparty:home'))

def my_party_view(request):
    if request.user.is_anonymous:
        return redirect(reverse('user:login'))
    myParties = TaxiParty.objects.filter(rider=request.user)
    context = {
        'partyList': myParties
    }
    return render(request, "myparty.html", context)
    