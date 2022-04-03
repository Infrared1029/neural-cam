from fastapi import FastAPI
import cv2
from starlette.responses import StreamingResponse
import torch
import mediapipe as mp
import numpy as np


from model import TransformerNet



FG_STYLE = None
BG_STYLE = None
keep_cam_on = True
cam = None



def to_torch_tensor(img_arr):
    img_arr = torch.from_numpy(img_arr).float()
    img_arr = img_arr.permute(2, 0, 1).unsqueeze(0)
    return img_arr
    
def to_numpy_array(img_arr):
    img_arr = img_arr.squeeze().permute(1, 2, 0)
    img_arr = img_arr.clamp(0, 255)
    img_arr = img_arr.numpy().astype('uint8')
    return img_arr



model_1 = TransformerNet().cuda()
model_2 = TransformerNet().cuda()
model_3 = TransformerNet().cuda()
model_4 = TransformerNet().cuda()
model_5 = TransformerNet().cuda()





model_1.load_state_dict(torch.load('models/scream_first.pth'))
model_2.load_state_dict(torch.load('models/starry_night.pth'))
model_3.load_state_dict(torch.load('models/wave.pth'))
model_4.load_state_dict(torch.load('models/untouched.pth'))
model_5.load_state_dict(torch.load('models/muse.pth'))




models = {
    'scream': model_1,
    'starry_night': model_2,
    'wave': model_3,
    'untouched': model_4,
    'muse': model_5,

}



app = FastAPI()



@app.get('/')
async def hello():
    global keep_cam_on
    keep_cam_on = True
    return StreamingResponse(gen(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.get('/turn_cam_off')
async def turn_cam_off():
    global keep_cam_on
    global FG_STYLE
    global BG_STYLE


    keep_cam_on = False
    FG_STYLE = None
    BG_STYLE = None

    try:
        cam.release()

    except:
        return {"cam": "camera is not turned on yet"}

    

    return {"cam": "off"}


@app.get('/set_fg_style/{style}')
async def set_fg_style(style: str):
    global FG_STYLE

    FG_STYLE = style
    return {'fg_style': FG_STYLE}

    
@app.get('/set_bg_style/{style}')
async def set_bg_style(style: str):
    global BG_STYLE

    BG_STYLE = style
    return {'bg_style': BG_STYLE}
    

@app.get('/reset_styles')
async def reset_styles():
    global BG_STYLE
    global FG_STYLE

    BG_STYLE = FG_STYLE = None    


mp_selfie_segmentation = mp.solutions.selfie_segmentation



def gen():

    global cam

    cam = cv2.VideoCapture(0)

    # ret, frame = cam.read()

    with mp_selfie_segmentation.SelfieSegmentation(
        model_selection=0) as selfie_segmentation:

            while keep_cam_on:


                ret, frame = cam.read()

                if FG_STYLE == None and BG_STYLE==None:
                    final_frame = frame
                

                elif FG_STYLE == BG_STYLE:
                    final_frame = to_torch_tensor(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    final_frame = models[FG_STYLE](final_frame.cuda())
                    final_frame = to_numpy_array(final_frame.detach().cpu())

                    final_frame = cv2.cvtColor(final_frame, cv2.COLOR_RGB2BGR)


                else:
                    results = selfie_segmentation.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
                    seg_mask = np.expand_dims((results.segmentation_mask > 0.5), axis=2)

                    if FG_STYLE == None:
                        fg_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    else:
                        fg_frame = to_torch_tensor(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                        fg_frame = models[FG_STYLE](fg_frame.cuda())
                        fg_frame = to_numpy_array(fg_frame.detach().cpu())
                        

                    if BG_STYLE == None:
                        bg_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  

                    else:  
                        bg_frame = to_torch_tensor(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                        bg_frame = models[BG_STYLE](bg_frame.cuda())
                        bg_frame = to_numpy_array(bg_frame.detach().cpu())
                    
                
                    final_frame = (fg_frame * seg_mask) + (bg_frame * ~seg_mask)
                    final_frame = cv2.cvtColor(final_frame, cv2.COLOR_RGB2BGR)


                flag, encoded_frame = cv2.imencode('.jpg', final_frame)

                if not flag: 
                    continue

                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                    bytearray(encoded_frame) + b'\r\n')

    cam.release()

