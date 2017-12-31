============= 
AQ3D Injector 
=============
About 
-------- 

I created this project to understand how the AQ3D application works
with the ability to inject commands to either the command and
server. The injector works by performing a man-in-the-middle attack on
the encrypted json communications between the client application and
the server and inspecting the commands and responses that are
exchanged.

In its current state, it has the ability to:

- Print directly relevant messages to logged in player to the terminal. E.g. move and attacking commands.
- Log all captured commands to a file. E.g. other players and NPC's location updates.
- Automatically get loot items dropped in a loot bag. To use this, its necessary to specify the item id (an integer) into the code. Currently the Fangs and Blood Fangs are hard coded.
- Tracks locations of given NPC's within the current map. Currently it tracks the Ghoul Minion, but this can be changed by specifying the ids of the NPC of interest.
- A buggy implementation to attack tracked NPC's that are within a given range.

Caveat
-------- 

This code has been developed against the Android version of the game
(v 1.6.8 and 1.6.9), and not tested with any other version. As the
protocol used between the client and server evolves, this application
will also need to be updated.

To utilise the injector, its required to trick the application into
connecting to the injector instead of the remote server. Then the
injector will complete the connection. There are the following options:

- Perform ``arpspoof`` on the network to redirect the network traffic to a different host. 
- Update the ``hosts`` file on the host running AQ3D application. Would require rooting a phone.
- Update a local dns server to redirect traffic to a different host.

The state of this code is in no way a functional or stable bot for the
game, and its doubtful that it will ever get to that state. However,
any contributions would be welcome.

From initial investigations, a challenge has been identified where its
not possible to position the client. That is, its possible to fake the
location of the client on the server but the client application does
not have the ability to update the players location from remote
commands so it makes it difficult to automatically position the player
next to a monster to attack it. This is because the attacking process
is involved, and each attack is initiated by the client (which if it
thinks it too far away from the monster can get confused).

Example
-------- 

Run the script in ``tests/test_simple.py`` to see an example of the
injector running. When in test mode it does not attempt to connect to
the remote server and only replays some captured packets to show the
decoding.
