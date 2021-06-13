# Introducing MLDock :tada:

<p align="center">
 <img src="../.vuepress/public/mldock-herro-image.jpg" width="250" alt="mldock hero image">
</p>

As Data Scientists, docker can be both a huge enabler and a huge headache. And if you're a Data Scientist tasked with going end-to-end, you might find that Mlops and data ops take up 90% of your time.

Questions like .. "Which server, where to serve, how to maintain the code, how to maintain the model..." And so on. 

Nevermind the challenges of validating experiments, analyzing performance and generating insights for better algorithms. The real data science. :microscope: ;) 

If you've been dockerizing your ML models for a while or just recently picked up docker. You'll realize that:

- ML requires a few combinations of bash commands.
- ML systems require many combinations of services.
- Every ML platform finds a way to combine these differently.

If you're like me, you realize that docker gives you infinite options which produce infinite possibilities. MlDock's core goal is to **"streamline options while maximizing possibilities"**. 

What this means for us is:
(list features)

MlDock is designed as a modular system. The idea is mix and match, but more so alter where what you want. 
(How we achieve this - diagram) 
- Command line to support development
- Template based to get your started fast, with all conveniences baked in. 
- Platform helpers to ship your code to any cloud provider and run ML on any provider service.

Final word, we started with intention of support Serverless platforms and realized that with some minor tweaks we could ship code everywhere. From VMs to container services either manged by cloud vendor or built with kubernetes. 
