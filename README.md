# Introduciton

My attempt to create a toy blockchain using some Docker containers to simulate a network of nodes.

I started the development from https://github.com/dvf/blockchain. There you can find all the details about the simple blockchain implementation (i.e., what you find in miner/blockchain.py).

The dvf work did not include a way to handle the interaction between miners in a way similar to what happens in a real network (He assumes that you have to interact with the network of nodes through several manual http requests). In addition, each node responded with a json object, which I believe is not so easy to read. I presented all the interactions in the simulation quite clearly, I hope this explains what happens.

However, I made several changes to the original code, which I hope one day to document. The purpose of the changes is to make each miner compatible with the type of operation I wanted in my simulation.

Therefore, I made a simulator in which:

- All miners are informed of the miners available in the network.
- Some "members" (including miners) perform transactions.
- The miners do the proof-of-work.
- The miners run the consensus algorithm to update their chains and resolve possible forks.

To run this simulation, it is necessary to

- Install Docker.
- Go to the project folder.
- Run `docker-compose build && docker-compose up -d`.
- Run `docker container logs simulator -f`.

Now you should see:

https://user-images.githubusercontent.com/24619344/174492219-c2ff8421-0e58-4414-ba3d-484b802f6be6.MP4

I hope that the content is self-explanatory.

Run `docker compose stop` in order to stop the execution of the simulator.


I'm aware that the project could be interesting as an educational simulator, but I's far from perfect. I don't know if I will be able to improve it. Therefore, if you think that this project has potential, please contribute, it could be the opportunity to develop something to show what a blockchain and a cryptocurrency consist of.

I am aware that the project could be interesting as an educational simulator, but it is far from perfect. I don't know if I will be able to improve it. Therefore, if you think this project has potential, please contribute, it could be an opportunity to develop something that shows what a blockchain and cryptocurrency are all about.



