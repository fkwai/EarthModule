#%% [init]
import tensorflow as tf
import ee
import folium

# in cmdline:
# earthengine authenticate
ee.Initialize()

print(tf.__version__)
print(ee.__version__)
print(folium.__version__)

