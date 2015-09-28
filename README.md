Amazon Dash Button Practice Tracker
======
A simple python script to track my music practice using an Amazon dash button.
Due to the attempt to conserve power, the dash button needs to connect to your
wifi network when pressed. This allows us to detect the ARP Probe using a python
library called Scapy. Once we have detected the button press we can update a
Google Form using a service called Cloudstich.  

![Practice Tracker Document](http://imgur.com/jE7HVjy1)

## References
Thanks goes to Ted Benson and his great [tutorial](https://medium.com/@edwardbenson/how-i-hacked-amazon-s-5-wifi-button-to-track-baby-data-794214b0bdd8) to get started
