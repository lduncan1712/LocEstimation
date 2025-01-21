# LocEstimation

## Using Image Detection And GyroScopic Metadata, Track Objects, Placing The Data Into A Database, Then Estimate Their Relative Positions Using A Gradient Descent Algorithm And Custom Heuristic


### Step 1:
#### Taking A Video Of Surroundings, While Capturing An Image With GyroScopic Data Approximately Once Per Second, Then Using Image Detection To Track These Objects Allows Us To Convert Pixel Locations Within A Frame Into Cardinal Direction, And Gryoscopic Angles, From Which We Place Into The Database I Designed (Please Note Below, Each Line Of The Same Color Represents The Same Tree, And Displays How It Has Moved Within The Lens Between Photos)

<img src="https://github.com/lduncan1712/LocEstimation/blob/18d5b1b6a33b21b4f6b1ba300a80295bd4919138/visuals/shortened_output2-ezgif.com-speed.gif" width="500">
<img src="https://github.com/lduncan1712/LocEstimation/blob/7c3b344f808a4a4ad09c64491bf0ffa421d426d2/visuals/image.png" width=750>


### Step 2:
#### Since We Know Lines Of The Same Color Represent The Same Tree, With One Perspective Of Each Tree Being Taken By Each Photo, We Can Attempt To Estimate The Relative Location Of Each Tree (And Where Each Photo Was Taken By Minimizing The Distance Between Colored Lines, We Start By Randomly Positioning Photo Locations (Note Black Lines Refer To Error Within Below Heuristic)

![Inital Random Positions](https://github.com/lduncan1712/LocEstimation/blob/main/visuals/initial_random_pos.png)

### Heuristic
#### We Define Our Cost Function To The Length Of The Shortest Line That Intersects All Lines (Please find our calculation within this repo)
![Shortest Cost](https://github.com/lduncan1712/ShortestPolyIntersecting)

### Step 3:

