# VHS tape script for MathStore ODE Practice & Verification Demo
Output docs/demo.gif
Output docs/demo.mp4

Set Shell "bash"
Set FontSize 16
Set Width 900
Set Height 600
Set Theme "Catppuccin Macchiato"
Set Padding 20
Set PlaybackSpeed 1.0

# Launch practice quizzer with medium difficulty
Type "uv run mathstore practice ode --difficulty medium"
Enter
Sleep 2s

# Request a pedagogical hint
Type "hint"
Enter
Sleep 2s

# Provide correct explicit answer with arbitrary constant C1
Type "y = 2 + C1*exp(-2*x)"
Enter
Sleep 2.5s

# Provide answer with incorrect IVP constant
Type "1 + 5*exp(-2*x)"
Enter
Sleep 2.5s

# Provide correct IVP answer
Type "1 + 2*exp(-2*x)"
Enter
Sleep 2.5s

# Final problem with different constant letter 'C'
Type "(C + x**3/3)/x"
Enter
Sleep 3s
