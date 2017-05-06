"""
SevenTweets is twitter-like service where each participant controls
its own node. They are connected and known to each other by discovery.

All user data is always stored in its own node. Other nodes can search
and return data from other nodes and display them, but node that owns
data has to be online.
"""
from seventweets.app import app
