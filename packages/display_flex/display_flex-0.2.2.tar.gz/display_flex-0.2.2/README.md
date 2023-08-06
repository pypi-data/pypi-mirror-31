# display_flex

## Root Question !

Have you ever wondered, like me, why the heck it is not **easily** possible to display content side by side in the notebook so as to get a more compact output ?

Well this is a lightweight attempt to address this shortcoming.  
Hopefully people may find it convenient.

## Install

From terminal:
```
pip install display_flex
```


## In a nutshell

The display layout under the hood is the [CSS Flexbox](https://css-tricks.com/snippets/css/a-guide-to-flexbox/), as in the [ipywidgets](http://ipywidgets.readthedocs.io/en/stable/examples/Widget%20Styling.html) package.  
You have full flexibility to pass the CSS *Flexbox* options.  
Default values for the *Flexbox* configuration are `flex-flow: row wrap` and `margin: 0`.  

Read and run the [demo notebook](http://nbviewer.jupyter.org/urls/gitlab.com/oscar6echo/display-flex/raw/master/demo_display_flex.ipynb) for more info.  

## Examples

### 1- Dataframes

![](img/display_flex_df.png)

### 2 - Any content

![](img/display_flex_any_content.png)



<!-- pandoc --from=markdown --to=rst --output=README.rst README.md -->
