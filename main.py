import requests
import json
import base64
import os
import streamlit as st
import pandas as pd
def save_image(image_data, filename):
    # Write the image_data to a new file with the given filename
    with open(filename, "wb") as f:
        f.write(image_data)
    print(f"Image saved as {filename}")
    # st.write(f"Image saved as {filename}")


def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"File {file_path} deleted successfully.")
    except OSError as e:
        print(f"Error deleting {file_path}: {e}")


def asticaAPI(endpoint, payload, timeout):
    response = requests.post(endpoint, data=json.dumps(payload), timeout=timeout,
                             headers={'Content-Type': 'application/json', })
    if response.status_code == 200:
        return response.json()
    else:
        return {'status': 'error', 'error': 'Failed to connect to the API.'}


asticaAPI_key = st.secrets['astica_key'] # visit https://astica.ai
asticaAPI_timeout = 35  # seconds  Using "gpt" or "gpt_detailed" will increase response time.

asticaAPI_endpoint = 'https://vision.astica.ai/describe'
asticaAPI_modelVersion = '2.0_full'  # '1.0_full', '2.0_full', or '2.1_full'

# Input Method 1: https URL of a jpg/png image (faster)
# asticaAPI_input = 'https://www.astica.org/inputs/analyze_3.jpg'
st.title("Image Uploader App")
st.write("Please upload an image.")
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    image_data = uploaded_file.read()
    # st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)
    save_image(image_data, "saved_image.png")

#Input Method 2: base64 encoded string of a local image (slower)
    path_to_local_file = 'saved_image.png';
    with open(path_to_local_file, 'rb') as file:
        image_data = file.read()
    image_extension = os.path.splitext(path_to_local_file)[1]
    #For now, let's make sure to prepend appropriately with: "data:image/extension_here;base64"
    asticaAPI_input = f"data:image/{image_extension[1:]};base64,{base64.b64encode(image_data).decode('utf-8')}"


    asticaAPI_visionParams = 'describe_all'  # comma separated options; leave blank for all; note "gpt" and "gpt_detailed" are slow.
    # '''
    #     '1.0_full' supported options:
    #         description
    #         objects
    #         categories
    #         moderate
    #         tags
    #         brands
    #         color
    #         faces
    #         celebrities
    #         landmarks
    #         gpt new (Slow - be patient)
    #         gpt_detailed new (Much Slower)
    #
    #     '2.0_full' supported options:
    #         description
    #         objects
    #         tags
    #         describe_all new
    #         text_read new
    #         gpt new (Slow - be patient)
    #         # gpt_detailed new (Much Slower)
    #
    #     '2.1_full' supported options:
    #         Supports all options
    #
    # '''

    # Define payload dictionary
    asticaAPI_payload = {
        'tkn': asticaAPI_key,
        'modelVersion': asticaAPI_modelVersion,
        'visionParams': asticaAPI_visionParams,
        'input': asticaAPI_input,
    }

    # Call API function and store result
    asticaAPI_result = asticaAPI(asticaAPI_endpoint, asticaAPI_payload, asticaAPI_timeout)

    # Display the original asticaAPI_result dictionary as JSON
    st.write("API Result:", asticaAPI_result)

    # Display key-value pairs of the asticaAPI_result dictionary
    for key, value in asticaAPI_result.items():
        st.write(f"{key}: {value}")
    print('\nastica API Output:')
    # print(json.dumps(asticaAPI_result, indent=4))
    st.write(json.dumps(asticaAPI_result, indent=4))
    # result_df = pd.DataFrame.from_dict(asticaAPI_result)
    # st.dataframe(result_df)
    # print('=================')
    # print('=================')

    # Handle asticaAPI response
    if 'status' in asticaAPI_result:
        # Output Error if exists
        if asticaAPI_result['status'] == 'error':
            print('Output:\n', asticaAPI_result['error'])
        # Output Success if exists
        if asticaAPI_result['status'] == 'success':
            if 'caption_GPTS' in asticaAPI_result and asticaAPI_result['caption_GPTS'] != '':
                print('=================')
                print('GPT Caption:', asticaAPI_result['caption_GPTS'])
            if 'caption' in asticaAPI_result and asticaAPI_result['caption']['text'] != '':
                print('=================')
                print('Caption:', asticaAPI_result['caption']['text'])
            if 'CaptionDetailed' in asticaAPI_result and asticaAPI_result['CaptionDetailed']['text'] != '':
                print('=================')
                print('CaptionDetailed:', asticaAPI_result['CaptionDetailed']['text'])
            if 'objects' in asticaAPI_result:
                print('=================')
                print('Objects:', asticaAPI_result['objects'])
    else:
        print('Invalid response')
        st.write('Invalid Response')


    delete_file(path_to_local_file)
