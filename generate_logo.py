from PIL import Image,ImageDraw,ImageFont
import base64,io
img=Image.new('RGB',(64,64),(0,123,255))
d=ImageDraw.Draw(img)
f=ImageFont.load_default()
w,h=d.textsize('LOGO',font=f)
d.text(((64-w)/2,(64-h)/2),'LOGO',fill='white',font=f)
buf=io.BytesIO()
img.save(buf,'PNG')
print(base64.b64encode(buf.getvalue()).decode())
