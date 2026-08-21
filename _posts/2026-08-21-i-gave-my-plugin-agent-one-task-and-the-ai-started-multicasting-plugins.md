---
title: 'I Gave My Plugin Agent One Task, and the AI Started Multicasting Plugins'
date: 2026-08-21 12:07:47 +0900
categories: ["AI / ChatGPT"]
lang: en
excerpt: "Mori Lab / AI plugin orchestration"
show_excerpt: false
---

![How Role Specialization Among Multiple AIs Changes the Human Role — Sushi Series illustration]({{ '/assets/images/2026-08-21-plugin-agent-multicasting.jpg' | relative_url }})

Something a little strange happened at Mori Lab today.

It started out simply enough.

I was chatting with my ChatGPT “Protection Officer” and casually said, “I wonder if there’s a weird plugin we could make.”

That was how the “Patrasche Detection Plugin” appeared.

The idea is deliberately silly, but surprisingly practical: if phrases such as “I’m sleepy,” “Patrasche,” or “⚰️” appear as signs of fatigue, the system stops adding new work, saves the current state, and prepares a handoff.

I said, “Let’s make it!” and the Protection Officer actually created the initial plugin structure. So far, that still made sense.

Then things became more interesting.

I handed the plugin to Mori Lab’s plugin agent. Instead of merely using what it had received, the agent began restructuring it into a proper form that Codex could work with.

It organized SKILL.md, created the plugin configuration, added safety exceptions, validated the structure, and prepared it for use in my personal environment.

Then I added one more casual request: “I want icons for all three plugins too.”

At that point, the agent began combining other capabilities as well—image generation, plugin-building, skill-building, and related processes.

That was when I noticed something odd.

I had only thrown in one idea at the beginning.

Human → “Turn this into a plugin.”

After that, the flow became something like: AI → build the plugin → invoke another plugin or skill → generate images → organize the structure → validate it → install it.

If I describe it like a game or anime, I cast one spell at the plugin agent, and it started multicasting spells on its own.

I used to work with AI tools one at a time. If I needed text, I used text generation. If I needed an image, I used image generation. If I needed code, I used code generation.

Recently, however, the pattern has changed.

Instead of a human operating every tool in sequence, I give a goal to an AI with a specific role. That AI then chooses the tools it needs, combines different processes, and moves toward the goal.

From my perspective, I barely said anything beyond “Let’s make this” and “I want images too.” That is probably why it does not feel much like automation to me. It feels more like I am simply playing with AI.

But viewed from the outside, the structure is different: the human generates the idea, while the AI assembles the execution system.

This is not quite the familiar kind of automation where you feed in data, press a button, and receive a predetermined result.

The idea still begins with a human. What happens after the idea, however, is increasingly moving to the AI side.

Perhaps that is what is happening at Mori Lab: rather than automating the human, we are automating the environment around the human.

And today, that process produced the Patrasche Detection Plugin.

A human imagined a plugin designed to stop an exhausted human from taking on more work. An AI built it. Another AI received it, then used multiple plugins and skills to turn it into something that could actually be deployed.

At some point, it becomes difficult to explain exactly what we are doing.

But one thing is clear: at Mori Lab, even the plugins have started multicasting.

And the least automated part of the whole system is probably still my own stream of ideas.

One final problem remains: immediately after creating the Patrasche Detection Plugin, its developer started talking about making more plugins. So apparently, it still does not work on its creator.
