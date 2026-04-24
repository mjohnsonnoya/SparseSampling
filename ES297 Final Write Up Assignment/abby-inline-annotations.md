## Detailed comments
 * Page 1 (Abstract): "makes them good candidates for improving energy transmission." -- this energy transmission motivation seems like a nod to application, but doesn't seem to actually matter for your study - perhaps worth removing this and just stating the value of STM/QPI imaging upfront, especially if this is going into a physics-specific journal ?

 * Page 1 (Abstract): "tip drift scales linearly with time." -- might be useful to provide a representative example of non-linear drift here, or at the end of the next sentence, to emphasize how useful and important your method is - for example, does your method work when there is a big "event" where the tip drifts a large distance but is stable otherwise?

 * Page 1 (Introduction): "ARPES" -- i think there's some recent work to make ARPES possible in local magnetic fields (perhaps yu he's group at yale, zx shen at stanford) - so it might be useful to re-iterate the specific advantages of QPI by saying something like "ARPES, which does not simultaneously resolve both real and momentum space" ?

 * Page 1 (Introduction): "We" -- is "We" here your team / Hoffman group, or generally the field of STM?

 * Page 1 (Introduction): "compressed sensing (CS)." -- does CS need a citation or is it a common field terminology?

 * Page 1 (Introduction): "nonlinear." -- similar comment to the abstract, it might be informative to provide an example or two of non-linear drift that can happen in a real experiment

 * Page 1 (Introduction): "the compressed sensing method" -- could be helpf to clarify if this is "our" (your) compressed sensing method? or if there is an existing method called "The" compressed sensing method?

 * Page 1 (Introduction): "BPDN" -- is this new or does it need to be cited ?

 * Page 1 (Introduction): "LASSO" -- what is lasso (citation) ?

 * Page 1 (Introduction): "And" -- typo ?

 * Page 2 (Introduction): "ℓ2 constraint" -- what's l2? (obvs feel free to leave if it's well known in the field, but if it's a niche term or doesn't need to be explained in your main text, can you just say "a key constraint" and then redirect to the appendix for more details as you already have?)

 * Page 2 (Drift Correction): "before or after" -- is this meant to be before AND after ? i'm a bit confused on the challenge you are explaining here

 * Page 2 (Methods):
   > FIG. 1.

   i quite like this figure, very clear and super cool results! one reading comment - i imagine most readers will want to look carefully at the differences between panels c/d and g/h, but they're quite hard to inspect closely due to how small the features are when placed in a single column figure like this. i'm not sure about your formatting or journal submission requirements, but is there any way to either make this span 2 columns or rearrange the panels so they're all bigger and easier to inspect?

 * Page 2 (Methods): "Bi2Sr2CaCu2O8 + δ." -- typo w/subscripts

 * Page 2 (Methods): "8 nm." -- imo the scale bar in the middle right of the images is a bit distracting compared to say bottom right of the image, but not sure if this is a standard for your lab so feel free to ignore...

 * Page 2 (Methods): "(QPI) scattering wavevectors and Bragg peaks" -- could be useful to label which are bragg peaks and which are qpi signal in the fig ?

 * Page 2 (Methods): "BSCCO" -- not sure if u need to re-define BSCCO in the main text and/or beginning of this figure caption?

 * Page 2 (Compressed Sensing): "nyquist" -- typo capitalize?

 * Page 2 (Compressed Sensing):
   > ϵ controls the allowable data-fidelity error and reflects the estimated noise level in the QPI measurements.

   perhaps useful to define this earlier after equation 1 ?

 * Page 3 (Compressed Sensing):
   > either by localizing key features in real space (e.g., near impurities) or by filtering in Fourier space around Bragg or QPI peaks

   some conceptual questions tat came up for me - how do you generate this selective map without knowing particular areas of interest apriori? do you get these impurities etc from the topography map? also, what if some random drift causes these areas to move out of the region where they are expected ?

 * Page 3 (Discussion): "traveling salesman problem" -- since you mention traveling salesman again later, can you explain briefly what this is within the text here?

 * Page 3 (Discussion): "adaptive sparse sampling" -- can use acronym

 * Page 3 (Discussion):
   > FIG. 2.

   for aesthetic consistency, it would be nice to have the color bars on the same side of the figure (left vs right) between all of your figures. also, is H vs L high versus low? i personally don't think H vs L needs to be written on the color bars, but if it's a field or lab standard then perhaps specifying H vs L in the caption would be helpful

 * Page 3 (Discussion): "Reconstructe" -- also just to confirm, this is the same reconstructed map from figure 1? would be good to label and explain

 * Page 3 (Discussion): "the QPI features appear sharper after correction." -- from my untrained eye, it's not immediately obvious to me which features i'm looking for that correspond to QPI, both in panels b and d - i think labeling those features either here or in fig 1 as mentioned would be helpful to re emphasize your point. of course you can also run into the problem of overlabeling where you "draw the readers eye" to something that doesn't really exist, but i think your data looks strong enough to show your point if you add an arrow/circle or two around representative features

 * Page 3 (Discussion):
   > The key point is that the full-grid topography map has the exact same tip movement history and pixel registration as the sparsely sampled map, ensuring they share the same drift maps

   this sentence was super clear and helped clarify what you were explaining earlier; i think the figure you mentioned in the email will also be really informative to support this discussion

 * Page 3 (Discussion): "L2" -- is this capital L2 the same as the lowercase l2 from before?

 * Page 3 (Discussion): "Adaptive sparse sampling (ASS)" -- brutal acronym lol... i really liked this paragraph though it was extremely clear

 * Page 4 (Adaptive Sparse Sampling):
   > "

   typo ?

 * Page 4 (Adaptive Sparse Sampling): "Pedagogical illustration of drift correction" -- based on the order of topics that you discuss in the paper, it seems like the drift correction figure would be better placed earlier as figure 3 and on the previous page if possible ?

 * Page 4 (Adaptive Sparse Sampling): "the literature could be improved," -- what is "the literature" - your work? or existing literature? to me it seems a bit funky to explicitly critique lack of existing literature, since my understanding is that your work is replacing LASSO or BPDN - but please correct me if i'm wrong...

 * Page 5 (Results): "RESULTS" -- i was confused that the results showed up here after all the discussion about the limitations of your technique etc. also, it seemed like your previous figures were already examples f you results. see document with the peer review, bu imo this paper will be much stronger if this section is rearranged and included earlier rather than right at the end

 * Page 5 (Results): "we've" -- language too casual ?

 * Page 5 (Results): "blue (noise floor) and red (signal)." -- can you make the colors match between panels a and b? i assume that the red area in both panels are supposed to refer to the same thing, but it looks orange in panel b so i got confused how they were supposed to match each other

 * Page 5 (Results): "positions" -- maybe pixels instead of positions? since that's the axis used in your panel b

 * Page 5 (Results):
   > It may be possible to achieve such good results with even fewer points through adaptive sparse sampling.

   i'm confused by this sentence - i thought you already showed the results of adaptive sparse sampling in fig 3?

 * Page 6 (Acknowledgements): "BPDN and LASSO" -- see review document, imo BPDN and LASSO throughout the manuscript are a bit distracting from the key method that you are demonstrating - BUT i think this is a great place to put all that information, and this paragraph is quite relevant and written very clearly

 * Page 7 (Adaptive Sparse Sampling): "[1]" -- see review document but it seems like there are some key areas that addl citations would be helpful

