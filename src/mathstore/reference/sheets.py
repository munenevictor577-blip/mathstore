"""Curated mathematical reference cheat sheets for university students."""

REFERENCE_TOPICS: dict[str, dict[str, str]] = {
    "derivatives": {
        "title": "Derivatives & Differentiation Rules",
        "description": "Common derivative rules and standard function derivatives",
        "text": """=== Derivatives Reference Cheat Sheet ===

Rules:
  Power Rule:        d/dx (x^n) = n*x^(n-1)
  Product Rule:      d/dx (u*v) = u'*v + u*v'
  Quotient Rule:     d/dx (u/v) = (u'*v - u*v') / v^2
  Chain Rule:        d/dx (f(g(x))) = f'(g(x)) * g'(x)

Common Functions:
  Exponential:       d/dx (e^x) = e^x
                     d/dx (a^x) = a^x * ln(a)
  Logarithmic:       d/dx (ln|x|) = 1/x
                     d/dx (log_a(x)) = 1 / (x * ln(a))
  Trigonometric:     d/dx (sin x) = cos x
                     d/dx (cos x) = -sin x
                     d/dx (tan x) = sec^2(x)
                     d/dx (cot x) = -csc^2(x)
                     d/dx (sec x) = sec(x)*tan(x)
                     d/dx (csc x) = -csc(x)*cot(x)
  Inverse Trig:      d/dx (arcsin x) = 1 / sqrt(1 - x^2)
                     d/dx (arccos x) = -1 / sqrt(1 - x^2)
                     d/dx (arctan x) = 1 / (1 + x^2)
  Hyperbolic:        d/dx (sinh x) = cosh x
                     d/dx (cosh x) = sinh x
                     d/dx (tanh x) = sech^2(x)""",
        "latex": r"""\section*{Derivatives Reference Cheat Sheet}

\subsection*{Differentiation Rules}
\begin{align*}
\text{Power Rule:} & \quad \frac{d}{dx}\left[x^n\right] = n x^{n-1} \\
\text{Product Rule:} & \quad \frac{d}{dx}[uv] = u'v + uv' \\
\text{Quotient Rule:} & \quad \frac{d}{dx}\left[\frac{u}{v}\right] = \frac{u'v - uv'}{v^2} \\
\text{Chain Rule:} & \quad \frac{d}{dx}[f(g(x))] = f'(g(x)) \cdot g'(x)
\end{align*}

\subsection*{Standard Derivatives}
\begin{align*}
\frac{d}{dx}[e^x] &= e^x & \frac{d}{dx}[a^x] &= a^x \ln(a) \\
\frac{d}{dx}[\ln|x|] &= \frac{1}{x} & \frac{d}{dx}[\log_a(x)] &= \frac{1}{x \ln(a)} \\
\frac{d}{dx}[\sin(x)] &= \cos(x) & \frac{d}{dx}[\cos(x)] &= -\sin(x) \\
\frac{d}{dx}[\tan(x)] &= \sec^2(x) & \frac{d}{dx}[\cot(x)] &= -\csc^2(x) \\
\frac{d}{dx}[\sec(x)] &= \sec(x)\tan(x) & \frac{d}{dx}[\csc(x)] &= -\csc(x)\cot(x) \\
\frac{d}{dx}[\arcsin(x)] &= \frac{1}{\sqrt{1 - x^2}} & \frac{d}{dx}[\arctan(x)] &= \frac{1}{1 + x^2} \\
\frac{d}{dx}[\sinh(x)] &= \cosh(x) & \frac{d}{dx}[\cosh(x)] &= \sinh(x)
\end{align*}""",
    },
    "integrals": {
        "title": "Integrals & Anti-derivatives",
        "description": "Standard integration rules, tables, and integration by parts",
        "text": """=== Integrals Reference Cheat Sheet ===

Rules:
  Power Rule:        ∫ x^n dx = x^(n+1)/(n+1) + C   (for n ≠ -1)
  Logarithmic:       ∫ 1/x dx = ln|x| + C
  By Parts:          ∫ u dv = u*v - ∫ v du

Common Functions:
  Exponential:       ∫ e^(ax) dx = (1/a)*e^(ax) + C
                     ∫ a^x dx = a^x / ln(a) + C
  Trigonometric:     ∫ sin(x) dx = -cos(x) + C
                     ∫ cos(x) dx = sin(x) + C
                     ∫ sec^2(x) dx = tan(x) + C
                     ∫ csc^2(x) dx = -cot(x) + C
                     ∫ sec(x)*tan(x) dx = sec(x) + C
                     ∫ tan(x) dx = -ln|cos(x)| + C = ln|sec(x)| + C
                     ∫ cot(x) dx = ln|sin(x)| + C
  Inverse Trig Forms:
                     ∫ 1 / (1 + x^2) dx = arctan(x) + C
                     ∫ 1 / sqrt(1 - x^2) dx = arcsin(x) + C
                     ∫ 1 / (a^2 + x^2) dx = (1/a)*arctan(x/a) + C
                     ∫ 1 / sqrt(a^2 - x^2) dx = arcsin(x/a) + C""",
        "latex": r"""\section*{Integrals Reference Cheat Sheet}

\subsection*{Integration Rules}
\begin{align*}
\text{Power Rule:} & \quad \int x^n \, dx = \frac{x^{n+1}}{n+1} + C \quad (n \neq -1) \\
\text{Logarithmic:} & \quad \int \frac{1}{x} \, dx = \ln|x| + C \\
\text{Integration by Parts:} & \quad \int u \, dv = uv - \int v \, du
\end{align*}

\subsection*{Standard Integrals}
\begin{align*}
\int e^{ax} \, dx &= \frac{1}{a} e^{ax} + C & \int a^x \, dx &= \frac{a^x}{\ln(a)} + C \\
\int \sin(x) \, dx &= -\cos(x) + C & \int \cos(x) \, dx &= \sin(x) + C \\
\int \sec^2(x) \, dx &= \tan(x) + C & \int \csc^2(x) \, dx &= -\cot(x) + C \\
\int \tan(x) \, dx &= \ln|\sec(x)| + C & \int \cot(x) \, dx &= \ln|\sin(x)| + C \\
\int \frac{1}{a^2 + x^2} \, dx &= \frac{1}{a}\arctan\left(\frac{x}{a}\right) + C & \int \frac{1}{\sqrt{a^2 - x^2}} \, dx &= \arcsin\left(\frac{x}{a}\right) + C
\end{align*}""",
    },
    "trig": {
        "title": "Trigonometric Identities",
        "description": "Core trigonometric identities (Pythagorean, angle sum, double angle, half angle)",
        "text": """=== Trigonometric Identities Cheat Sheet ===

Pythagorean Identities:
  sin^2(x) + cos^2(x) = 1
  1 + tan^2(x) = sec^2(x)
  1 + cot^2(x) = csc^2(x)

Angle Sum & Difference:
  sin(A ± B) = sin(A)*cos(B) ± cos(A)*sin(B)
  cos(A ± B) = cos(A)*cos(B) ∓ sin(A)*sin(B)
  tan(A ± B) = (tan(A) ± tan(B)) / (1 ∓ tan(A)*tan(B))

Double Angle Formulas:
  sin(2x) = 2*sin(x)*cos(x)
  cos(2x) = cos^2(x) - sin^2(x) = 2*cos^2(x) - 1 = 1 - 2*sin^2(x)
  tan(2x) = 2*tan(x) / (1 - tan^2(x))

Half Angle / Power Reduction:
  sin^2(x) = (1 - cos(2x)) / 2
  cos^2(x) = (1 + cos(2x)) / 2
  tan^2(x) = (1 - cos(2x)) / (1 + cos(2x))

Euler's Formula:
  e^(i*x) = cos(x) + i*sin(x)""",
        "latex": r"""\section*{Trigonometric Identities Cheat Sheet}

\subsection*{Pythagorean Identities}
\begin{align*}
\sin^2(x) + \cos^2(x) &= 1 \\
1 + \tan^2(x) &= \sec^2(x) \\
1 + \cot^2(x) &= \csc^2(x)
\end{align*}

\subsection*{Angle Sum and Difference}
\begin{align*}
\sin(A \pm B) &= \sin(A)\cos(B) \pm \cos(A)\sin(B) \\
\cos(A \pm B) &= \cos(A)\cos(B) \mp \sin(A)\sin(B) \\
\tan(A \pm B) &= \frac{\tan(A) \pm \tan(B)}{1 \mp \tan(A)\tan(B)}
\end{align*}

\subsection*{Double Angle Formulas}
\begin{align*}
\sin(2x) &= 2\sin(x)\cos(x) \\
\cos(2x) &= \cos^2(x) - \sin^2(x) = 2\cos^2(x) - 1 = 1 - 2\sin^2(x) \\
\tan(2x) &= \frac{2\tan(x)}{1 - \tan^2(x)}
\end{align*}

\subsection*{Power Reduction (Half Angle)}
\begin{align*}
\sin^2(x) &= \frac{1 - \cos(2x)}{2} & \cos^2(x) &= \frac{1 + \cos(2x)}{2}
\end{align*}

\subsection*{Euler's Formula}
\[
e^{ix} = \cos(x) + i\sin(x)
\]""",
    },
    "limits": {
        "title": "Limits & Indeterminate Forms",
        "description": "Standard limits, L'Hôpital's Rule, and indeterminate forms",
        "text": """=== Limits Reference Cheat Sheet ===

Standard Limits:
  lim (x->0)  sin(x) / x = 1
  lim (x->0)  (1 - cos(x)) / x = 0
  lim (x->0)  (e^x - 1) / x = 1
  lim (x->0)  ln(1 + x) / x = 1
  lim (x->∞)  (1 + 1/x)^x = e
  lim (x->0)  (1 + x)^(1/x) = e

L'Hôpital's Rule:
  If lim f(x)/g(x) produces 0/0 or (±∞)/(±∞), then:
    lim f(x)/g(x) = lim f'(x)/g'(x)
  (provided the derivative limit exists)

Indeterminate Forms:
  Quotients:   0/0,  (±∞)/(±∞)
  Products:    0 * (±∞)          (rewrite as 0/(1/∞) or ∞/(1/0))
  Differences: ∞ - ∞             (combine fractions / conjugate)
  Powers:      0^0,  1^∞,  ∞^0   (use y = f(x)^g(x) => ln(y) = g(x)*ln(f(x)))""",
        "latex": r"""\section*{Limits Reference Cheat Sheet}

\subsection*{Standard Limits}
\begin{align*}
\lim_{x \to 0} \frac{\sin(x)}{x} &= 1 & \lim_{x \to 0} \frac{1 - \cos(x)}{x} &= 0 \\
\lim_{x \to 0} \frac{e^x - 1}{x} &= 1 & \lim_{x \to 0} \frac{\ln(1 + x)}{x} &= 1 \\
\lim_{x \to \infty} \left(1 + \frac{1}{x}\right)^x &= e & \lim_{x \to 0} (1 + x)^{1/x} &= e
\end{align*}

\subsection*{L'Hôpital's Rule}
\[
\text{If } \lim_{x \to c} \frac{f(x)}{g(x)} \in \left\{ \frac{0}{0}, \frac{\pm\infty}{\pm\infty} \right\}, \quad \text{then } \lim_{x \to c} \frac{f(x)}{g(x)} = \lim_{x \to c} \frac{f'(x)}{g'(x)}
\]

\subsection*{Indeterminate Forms}
\begin{itemize}
  \item \textbf{Quotient Forms:} $\frac{0}{0}$, $\frac{\pm\infty}{\pm\infty}$
  \item \textbf{Product Forms:} $0 \cdot \infty$ (transform to quotient)
  \item \textbf{Difference Forms:} $\infty - \infty$ (combine / rationalize)
  \item \textbf{Exponential Forms:} $0^0$, $1^\infty$, $\infty^0$ (apply logarithmic transformation: $\ln y = g(x)\ln f(x)$)
\end{itemize}""",
    },
    "series": {
        "title": "Taylor & Maclaurin Series",
        "description": "Common series expansions, radii of convergence, and general formula",
        "text": """=== Taylor & Maclaurin Series Cheat Sheet ===

General Formula (Taylor series about x = a):
  f(x) = Σ [ f^(n)(a) / n! ] * (x - a)^n
       = f(a) + f'(a)*(x - a) + f''(a)/2! *(x - a)^2 + ...

Common Maclaurin Series (about x = 0):
  e^x       = Σ x^n / n!                 = 1 + x + x^2/2! + x^3/3! + ...       (R = ∞)
  sin(x)    = Σ (-1)^n * x^(2n+1)/(2n+1)! = x - x^3/3! + x^5/5! - ...          (R = ∞)
  cos(x)    = Σ (-1)^n * x^(2n)/(2n)!     = 1 - x^2/2! + x^4/4! - ...          (R = ∞)
  1 / (1-x) = Σ x^n                      = 1 + x + x^2 + x^3 + ...             (R = 1, |x| < 1)
  ln(1+x)   = Σ (-1)^(n+1) * x^n / n     = x - x^2/2 + x^3/3 - x^4/4 + ...     (R = 1, -1 < x ≤ 1)
  arctan(x) = Σ (-1)^n * x^(2n+1)/(2n+1) = x - x^3/3 + x^5/5 - ...             (R = 1, |x| ≤ 1)
  sinh(x)   = Σ x^(2n+1) / (2n+1)!        = x + x^3/3! + x^5/5! + ...          (R = ∞)
  cosh(x)   = Σ x^(2n) / (2n)!            = 1 + x^2/2! + x^4/4! + ...          (R = ∞)""",
        "latex": r"""\section*{Taylor \& Maclaurin Series Cheat Sheet}

\subsection*{General Formula}
\[
f(x) = \sum_{n=0}^{\infty} \frac{f^{(n)}(a)}{n!} (x - a)^n = f(a) + f'(a)(x - a) + \frac{f''(a)}{2!}(x - a)^2 + \cdots
\]

\subsection*{Common Maclaurin Series ($a = 0$)}
\begin{align*}
e^x &= \sum_{n=0}^{\infty} \frac{x^n}{n!} = 1 + x + \frac{x^2}{2!} + \frac{x^3}{3!} + \cdots & (-\infty < x < \infty) \\
\sin(x) &= \sum_{n=0}^{\infty} \frac{(-1)^n x^{2n+1}}{(2n+1)!} = x - \frac{x^3}{3!} + \frac{x^5}{5!} - \cdots & (-\infty < x < \infty) \\
\cos(x) &= \sum_{n=0}^{\infty} \frac{(-1)^n x^{2n}}{(2n)!} = 1 - \frac{x^2}{2!} + \frac{x^4}{4!} - \cdots & (-\infty < x < \infty) \\
\frac{1}{1 - x} &= \sum_{n=0}^{\infty} x^n = 1 + x + x^2 + x^3 + \cdots & (|x| < 1) \\
\ln(1 + x) &= \sum_{n=1}^{\infty} \frac{(-1)^{n+1} x^n}{n} = x - \frac{x^2}{2} + \frac{x^3}{3} - \cdots & (-1 < x \le 1) \\
\arctan(x) &= \sum_{n=0}^{\infty} \frac{(-1)^n x^{2n+1}}{2n+1} = x - \frac{x^3}{3} + \frac{x^5}{5} - \cdots & (|x| \le 1)
\end{align*}""",
    },
}

TOPIC_ALIASES: dict[str, str] = {
    "derivative": "derivatives",
    "diff": "derivatives",
    "integral": "integrals",
    "integrate": "integrals",
    "int": "integrals",
    "trigonometry": "trig",
    "identities": "trig",
    "limit": "limits",
    "taylor": "series",
    "maclaurin": "series",
}


def normalize_topic_name(topic: str) -> str:
    """Normalize user input topic and resolve aliases."""
    normalized = topic.strip().lower()
    return TOPIC_ALIASES.get(normalized, normalized)


def list_topics() -> dict[str, str]:
    """Return dictionary of topic names mapped to short descriptions."""
    return {name: data["description"] for name, data in REFERENCE_TOPICS.items()}


def list_topics_formatted() -> str:
    """Return a formatted string listing available reference topics."""
    lines = ["Available study reference topics:"]
    for name, data in REFERENCE_TOPICS.items():
        lines.append(f"  {name:<12} - {data['description']}")
    lines.append("\nUsage: mathstore ref <topic> [--latex]")
    return "\n".join(lines)


def get_reference(topic: str, latex: bool = False) -> str:
    """
    Retrieve reference content for a topic.

    Args:
        topic: Topic name or alias (e.g. 'derivatives', 'trig')
        latex: Whether to return LaTeX format instead of plain text

    Raises:
        ValueError: If the topic is not recognized.
    """
    key = normalize_topic_name(topic)
    if key not in REFERENCE_TOPICS:
        available = ", ".join(REFERENCE_TOPICS.keys())
        raise ValueError(
            f"Unknown reference topic '{topic}'. Available topics: {available}."
        )

    topic_data = REFERENCE_TOPICS[key]
    return topic_data["latex"] if latex else topic_data["text"]
