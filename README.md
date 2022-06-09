# Graphics Final Project
### Name: Qina Liu
### Class Period: 4
---
## New Graphics Engine Features
1. light mdl feature
2. set knobname value mdl feature
3. set additional frames parameters
4. light knob w/ gradient command

---
## The Details
3 - set knobname value [frame frame] 
    if one additional frame parameter is provided, only the knob for that frame will be set to the specified value 
    if two additional frame parameters are provided, the range from one frame to the next will be set to te value
    
4 - light can be given a knob, and the gradient command specifies how r,g,b values of light changes in animation
    light symbol x y z r g b [ knob ] - optional knob changes r,g,b 
    gradient knob startframe endframe changeInR changeInG changeInB
    
