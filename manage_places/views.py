from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from .models import PlacesData, FileModel
import random
import base64
import os
from imagekitio import ImageKit
from dotenv import load_dotenv
load_dotenv()




def landingPage(request):
    if request.method == 'GET':
        return render(request, 'manage_places/landing-page.html')
    else:
        city_name = request.POST["city"]
        return redirect('list/{}'.format(city_name))


def listPage(request, city_name):
    places_list = PlacesData.objects.filter(city_name=city_name, approval_status=True)
    alert_flag = False
    if len(places_list) == 0:
        alert_flag = True
    return render(request, 'manage_places/list-page.html',{
        "city_name": city_name,
        "place_list":places_list,
        "alert_flag":alert_flag
    })


def generate_uniq_id():
    # first i will define a character 
    # after that i will generate random characters
    final_uniq_id = ''
    characters_str = 'abcdefghijklmnopqrstuvwxyz0123456789'
    for x in range(10):
        final_uniq_id += random.choice(characters_str)
        
    return final_uniq_id


def addNewPlaces(request):
    if request.method == 'GET':
        alert_flag = False
        if request.GET.get('alert') == 'True':
            alert_flag = True
        return render(request, 'manage_places/add-new-places.html', {
            'alert_flag' : alert_flag,
            'alert_msg' : request.GET.get('msg')
        })
    else:
        place_id = generate_uniq_id()
        new_place = request.POST["enter-place-name"]
        place_type = request.POST["select-place-type"]
        city_name = request.POST["city"]
        gmap_link = request.POST["gmap-link"]

        # validate map link
        indx = gmap_link.find('https')
        gmap_link = gmap_link[indx:]
        if 'https://' not in gmap_link:
            return redirect('/add?alert=True&msg=please enter a valid google map url')

        # validate field
        if place_type=="None" or city_name=="None":
            return redirect('/add?alert=True&msg=please select valid city or place type')

        # https://www.jborowski.eu/2018/06/handling-files-upload-in-django-python-3-without-forms/ss
        # handling with the user image
        # 1. read the image from the add request 
        _, file = request.FILES.popitem()  # get first element of the uploaded files
        file = file[0]  # get the file from MultiValueDict

        # 2. write the image locally by saving to the model
        file_model = FileModel(file=file, file_id=place_id)
        file_model.save()

        # 3. Get the path of local image and upload the image to Imagekit API
        file_obj = FileModel.objects.get(file_id=place_id)
        file_path = file_obj.file.path

        # 3.1 Create base64 for the file
        with open(file_path, mode="rb") as img:
            imgstr = base64.b64encode(img.read())

        # 3.2 upload to imagekit API
        imagekit = ImageKit(
            private_key=os.environ.get("imagekit_private_key"),
            public_key=os.environ.get("imagekit_public_key"),
            url_endpoint=os.environ.get("imagekit_url_endpoint")
        )

        try:
            upload = imagekit.upload(
                file=imgstr,
                file_name= "_".join(new_place.split(' '))+"_"+place_id,
                options={
                    "response_fields": ["is_private_file", "folder"],
                    "folder" : city_name,
                },
            )
        except:
            os.remove(file_path)
            file_obj.delete()
            return redirect('/add?alert=True&msg=oops! something went wrong.')
            
        
        # 5. Now delete the file from local / model entry
        os.remove(file_path)
        file_obj.delete()

         # 6. Check the Imagekit API response 
        if upload.get("error") is not None:
            # add alert 
            return redirect('/add?alert=True&msg=oops! something went wrong.')

        # 7. if upload is success then save the imagekit url in PlacedData model along with other details like place name, etc
        img_url = upload.get('response').get('url')
        # now save all fields to model
        place_upvote = 0

        new_place_object = PlacesData(place_id=place_id, place_name=new_place, city_name=city_name, place_type=place_type,place_upvote=place_upvote,image_url=img_url,map_url=gmap_link)
        new_place_object.save()


        return redirect('/sub/{}'.format(place_id))



def subConfirmPage(request, place_id):
    try:
        place_obj = PlacesData.objects.get(place_id=place_id)
        return render(request, 'manage_places/submission-page.html', {'place_obj': place_obj})
    except:
        return redirect('add-new-places')
    


def placesApproval(request):
    if not request.user.is_superuser:
        return redirect("landing-page")
    places_list = PlacesData.objects.filter(approval_status=False)
    return render(request, 'manage_places/approve-new-places.html', {'places_list':places_list})


def upvoteView(request):
    place_id = request.GET.get('place_id')
    try:
        place_object = PlacesData.objects.get(place_id = place_id)
        place_object.place_upvote+=1
        place_object.save()
        return HttpResponse('Success!')
    except:
        return HttpResponse('Failed!')
    

def rejectView(request, place_id):
    if request.method == 'POST':
        place_obj = PlacesData.objects.get(place_id=place_id)
        place_obj.delete()
        return redirect('/up')


def acceptView(request, place_id):
    if request.method == 'POST':
        place_obj = PlacesData.objects.get(place_id=place_id)
        place_obj.approval_status = True
        place_obj.save()
        return redirect('/up')