# BlendKit

This repository aims at implementing a scalable and cost-effective solution for distributed animation rendering in Blender on diskless nodes.

The project currently focuses on the infrastructure rather than the actual software implementation.

## Components
- [Streamlit](https://github.com/streamlit/streamlit) - Frontend
- [NodeRED](https://nodered.org) - Backend
- [Ansible](https://docs.ansible.com) - Deployment & Automation

## References

- [Flamenco](https://flamenco.blender.org)
- [Brenda](https://github.com/jamesyonan/brenda/blob/master/brenda/utils.py)

## Commands

Render on MacOS

```bash
blender -b $SCENE -f 0 -- --cycles-device METAL --cycles-print-stats 
```
