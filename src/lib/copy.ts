import { FIRM } from "./content";
import type { Lang } from "./cities";

export interface Step {
  title: string;
  body: string;
}

export interface FormCopy {
  title: string;
  subtitle: (city: string) => string;
  firstName: string;
  lastName: string;
  phone: string;
  email: string;
  cityLabel: string;
  employer: string;
  optional: string;
  whatHappened: string;
  consent: string;
  submit: string;
  submitting: string;
  errFirst: string;
  errLast: string;
  errPhone: string;
  errEmail: string;
  errCity: string;
  errWhat: string;
  errConsent: string;
  genericError: string;
}

export interface Copy {
  locale: string;
  seoTitle: (city: string) => string;
  seoDescription: (city: string) => string;
  headline: (city: string) => string;
  subheadline: string;
  heroBullets: string[];
  ctaPrimary: string;
  ctaCall: string;
  proofTitle: string;
  proofGoogleRating: string;
  proofGoogleReviews: string;
  proofYelp: string;
  proofPoints: string[];
  trustBadgesTitle: string;
  trustMembershipsTitle: string;
  problemTitle: string;
  problemItems: string[];
  noWinTitle: string;
  noWinBody: string[];
  practiceTitle: string;
  practiceIntro: (city: string) => string;
  practiceAreas: string[];
  notSureTitle: string;
  notSureBody: string;
  stepsTitle: string;
  steps: Step[];
  testimonialsTitle: string;
  testimonialsIntro: string;
  testimonialsMore: string;
  attorneyTitle: string;
  attorneyName: string;
  attorneyRole: string;
  attorneyBio: string;
  officeCaption: string;
  teamCaption: string;
  finalTitle: string;
  finalBody: (city: string) => string;
  finalNote: string;
  finalStopTitle: string;
  finalStopBody: string;
  finalStopUrgency: string;
  finalStopNote: string;
  form: FormCopy;
  disclaimer: (city: string) => string;
  disclaimerGeneric: string;
  footerDisclaimer: string;
  footerOfficeTitle: string;
  footerContactTitle: string;
  thankYouTitle: string;
  thankYouBody: string;
  thankYouNote: string;
  switchLangLabel: string;
}

const en: Copy = {
  locale: "en_US",
  seoTitle: (city) => `Employment Lawyers Serving ${city} Employees | Free Consultation`,
  seoDescription: (city) =>
    `Fired, harassed, retaliated against, or underpaid at work in ${city}? Employment Law Assist helps California employees with wrongful termination, retaliation, discrimination, harassment, and unpaid wages. Free consultation.`,
  headline: (city) =>
    `Fired, Harassed, Retaliated Against, or Mistreated at Work in ${city}?`,
  subheadline:
    "Talk to an employment lawyer about what happened. We help California employees with wrongful termination, retaliation, discrimination, harassment, unpaid wages, and workplace mistreatment.",
  heroBullets: [
    "Free consultation",
    "No fee unless we win, if your case qualifies",
    "Hablamos Español",
    "Available 24/7 by phone",
  ],
  ctaPrimary: "Request a Free Consultation",
  ctaCall: `Call Now: ${FIRM.phoneDisplay}`,
  proofTitle: "Recognized and Highly Rated",
  proofGoogleRating: "4.8-Star Google Rating",
  proofGoogleReviews: "70+ Google Reviews",
  proofYelp: "Highly Rated on Yelp",
  proofPoints: ["Hablamos Español", "Available 24/7 by Phone", "Free Consultation"],
  trustBadgesTitle: "Recognized & Trusted",
  trustMembershipsTitle: "Proud Members Of",
  problemTitle: "Do Any of These Sound Familiar?",
  problemItems: [
    "You were fired after reporting harassment, discrimination, or unsafe conditions.",
    "You were let go after taking medical leave, getting injured, or filing a complaint.",
    "You're being harassed or discriminated against because of who you are.",
    "You're not being paid for all your hours, overtime, or missed meal and rest breaks.",
    "You were pushed out, demoted, or punished for standing up for your rights.",
  ],
  noWinTitle: "Free Consultation. No Fee Unless We Win.",
  noWinBody: [
    "Your first consultation is free. We handle qualifying cases on a contingency fee basis — you pay no attorney's fee unless we win or settle your case.",
    "If your case qualifies and we take it on, there's no out-of-pocket attorney's fee along the way.",
  ],
  practiceTitle: "How We Help Employees",
  practiceIntro: (city) =>
    `We represent employees in ${city} across a full range of California workplace claims.`,
  practiceAreas: [
    "Wrongful Termination",
    "Meal & Rest Break Violations",
    "Retaliation",
    "Discrimination",
    "Workers' Compensation",
    "Harassment",
  ],
  notSureTitle: "Not Sure If You Have a Case?",
  notSureBody:
    "That's exactly what the free consultation is for. Tell us what happened and the team will let you know if your situation may involve a California employment law claim.",
  stepsTitle: "What to Expect When You Contact Us",
  steps: [
    {
      title: "Tell us what happened",
      body: "Call or submit the form with a brief explanation of your workplace issue.",
    },
    {
      title: "The team reviews your situation",
      body: "Employment Law Assist will look at whether your situation may involve a California employment law claim.",
    },
    {
      title: "If your case qualifies, you learn the next steps",
      body: "If the firm can help, the team will explain what may happen next.",
    },
  ],
  testimonialsTitle: "What Clients Say",
  testimonialsIntro: "Real reviews from people we've helped.",
  testimonialsMore: "More reviews available on Google and Yelp.",
  attorneyTitle: "Meet Your Attorney",
  attorneyName: "Kasim Idrees",
  attorneyRole: "Founding Attorney, Employment Law Assist",
  attorneyBio:
    "Employment Law Assist is led by attorney Kasim Idrees, who represents California employees against unlawful treatment at work. The team works from our Woodland Hills office and serves employees across California.",
  officeCaption: "Our office in Woodland Hills, California",
  teamCaption: "Our team at work",
  finalTitle: "Talk to Someone About Your Situation Today",
  finalBody: (city) =>
    `Call now or request a free, confidential consultation. Serving employees in ${city} across California.`,
  finalNote: "Available 24/7 by phone. Hablamos Español.",
  finalStopTitle: "Still Wondering If What Happened Was Legal?",
  finalStopBody:
    "You do not need to know the exact legal category before reaching out. If you were fired, punished, harassed, underpaid, or treated unfairly at work, you can call or request a free consultation today.",
  finalStopUrgency: "Call now — consultation is free and confidential.",
  finalStopNote: "Free consultation. Hablamos Español. Available 24/7 by phone.",
  form: {
    title: "Request a Free Consultation",
    subtitle: (city) => `No commitment. Confidential. Serving employees in ${city}.`,
    firstName: "First name",
    lastName: "Last name",
    phone: "Phone",
    email: "Email",
    cityLabel: "City",
    employer: "Employer name",
    optional: "(optional)",
    whatHappened: "What happened?",
    consent:
      "I agree to be contacted by Employment Law Assist about my inquiry. I understand that contacting the firm does not create an attorney-client relationship.",
    submit: "Get My Free Consultation",
    submitting: "Submitting...",
    errFirst: "Enter your first name.",
    errLast: "Enter your last name.",
    errPhone: "Enter a valid phone number.",
    errEmail: "Enter a valid email address.",
    errCity: "Enter your city.",
    errWhat: "Tell us briefly what happened.",
    errConsent: "Please provide your consent to continue.",
    genericError: "Something went wrong. Please call us instead.",
  },
  disclaimer: (city) =>
    `The information on this page is for general informational purposes only and is not legal advice. Contacting Employment Law Assist does not create an attorney-client relationship. Employment Law Assist serves employees in ${city} and does not maintain a physical office in ${city}. Every case is different and prior results do not guarantee a similar outcome.`,
  disclaimerGeneric:
    "The information on this page is for general informational purposes only and is not legal advice. Contacting Employment Law Assist does not create an attorney-client relationship. Every case is different and prior results do not guarantee a similar outcome.",
  footerDisclaimer:
    "The information on this website is attorney advertising and is for general information only. Nothing here is legal advice for any individual case or situation. This information is not intended to create, and receipt or viewing does not constitute, an attorney-client relationship.",
  footerOfficeTitle: "Office",
  footerContactTitle: "Contact Us",
  thankYouTitle: "Thank you — we've received your request",
  thankYouBody:
    "A member of our team will review your information and reach out. If you'd like to speak with someone now, call us directly — we're available 24/7 by phone.",
  thankYouNote: "Hablamos Español",
  switchLangLabel: "Español",
};

const es: Copy = {
  locale: "es_US",
  seoTitle: (city) => `Abogados Laborales que Ayudan a Empleados en ${city} | Consulta Gratis`,
  seoDescription: (city) =>
    `¿Lo despidieron, acosaron, tomaron represalias o le pagaron mal en el trabajo en ${city}? Employment Law Assist ayuda a empleados de California con despido injustificado, represalias, discriminación, acoso y salarios no pagados. Consulta gratis.`,
  headline: (city) =>
    `¿Despedido, Acosado, con Represalias o Maltratado en el Trabajo en ${city}?`,
  subheadline:
    "Hable con un abogado laboral sobre lo que pasó. Employment Law Assist ayuda a empleados de California con despido injustificado, represalias, discriminación, acoso, salarios no pagados, horas extra y maltrato en el trabajo.",
  heroBullets: [
    "Consulta gratis",
    "Sin honorarios a menos que ganemos, si su caso califica",
    "Hablamos Español",
    "Disponible por teléfono 24/7",
  ],
  ctaPrimary: "Solicite una Consulta Gratis",
  ctaCall: `Llame Ahora: ${FIRM.phoneDisplay}`,
  proofTitle: "Reconocidos y Bien Calificados",
  proofGoogleRating: "Calificación 4.8 Estrellas en Google",
  proofGoogleReviews: "Más de 70 Reseñas en Google",
  proofYelp: "Bien Calificados en Yelp",
  proofPoints: ["Hablamos Español", "Disponible por Teléfono 24/7", "Consulta Gratis"],
  trustBadgesTitle: "Reconocidos y de Confianza",
  trustMembershipsTitle: "Miembros Orgullosos De",
  problemTitle: "¿Le Suena Familiar Algo de Esto?",
  problemItems: [
    "Lo despidieron después de reportar acoso, discriminación o condiciones inseguras.",
    "Lo despidieron después de tomar incapacidad médica, lesionarse o presentar una queja.",
    "Lo acosan o discriminan por quién es usted.",
    "No le pagan todas sus horas, horas extra o descansos de comida perdidos.",
    "Lo presionaron, degradaron o castigaron por defender sus derechos.",
  ],
  noWinTitle: "Consulta Gratis. Sin Honorarios a Menos que Ganemos.",
  noWinBody: [
    "Su primera consulta es gratis. Manejamos los casos que califican con honorarios de contingencia — usted no paga honorarios de abogado a menos que ganemos o resolvamos su caso.",
    "Si su caso califica y lo aceptamos, no hay honorarios de abogado de su bolsillo durante el proceso.",
  ],
  practiceTitle: "Cómo Ayudamos a los Empleados",
  practiceIntro: (city) =>
    `Representamos a empleados en ${city} con una amplia gama de reclamos laborales en California.`,
  practiceAreas: [
    "Despido Injustificado",
    "Violaciones de Descanso y Comida",
    "Represalias",
    "Discriminación",
    "Compensación Laboral",
    "Acoso",
  ],
  notSureTitle: "¿No Está Seguro Si Tiene un Caso?",
  notSureBody:
    "Para eso es la consulta gratis. Cuéntenos qué pasó y el equipo le dirá si su situación podría involucrar un reclamo bajo la ley laboral de California.",
  stepsTitle: "Qué Esperar Cuando Nos Contacta",
  steps: [
    {
      title: "Cuéntenos qué pasó",
      body: "Llame o envíe el formulario con una breve explicación de su problema laboral.",
    },
    {
      title: "El equipo revisa su situación",
      body: "Employment Law Assist evaluará si su situación podría involucrar un reclamo bajo la ley laboral de California.",
    },
    {
      title: "Si su caso califica, conoce los siguientes pasos",
      body: "Si la firma puede ayudar, el equipo le explicará qué podría suceder después.",
    },
  ],
  testimonialsTitle: "Lo que Dicen los Clientes",
  testimonialsIntro:
    "Reseñas reales de personas a las que hemos ayudado (en su idioma original, inglés).",
  testimonialsMore: "Más reseñas disponibles en Google y Yelp.",
  attorneyTitle: "Conozca a Su Abogado",
  attorneyName: "Kasim Idrees",
  attorneyRole: "Abogado Fundador, Employment Law Assist",
  attorneyBio:
    "Employment Law Assist está dirigida por el abogado Kasim Idrees, quien representa a empleados de California frente a tratos ilegales en el trabajo. El equipo trabaja desde nuestra oficina en Woodland Hills y ayuda a empleados en todo California.",
  officeCaption: "Nuestra oficina en Woodland Hills, California",
  teamCaption: "Nuestro equipo en acción",
  finalTitle: "Hable Hoy con Alguien Sobre Su Situación",
  finalBody: (city) =>
    `Llame ahora o solicite una consulta gratis y confidencial. Ayudamos a empleados en ${city} en todo California.`,
  finalNote: "Disponible por teléfono 24/7. Hablamos Español.",
  finalStopTitle: "¿Aún Se Pregunta Si Lo Que Pasó Fue Legal?",
  finalStopBody:
    "No necesita saber la categoría legal exacta antes de contactarnos. Si lo despidieron, castigaron, acosaron, le pagaron mal o lo trataron injustamente en el trabajo, puede llamar o solicitar una consulta gratis hoy.",
  finalStopUrgency: "Llame ahora — la consulta es gratis y confidencial.",
  finalStopNote: "Consulta gratis. Hablamos Español. Disponible por teléfono 24/7.",
  form: {
    title: "Solicite una Consulta Gratis",
    subtitle: (city) => `Sin compromiso. Confidencial. Ayudamos a empleados en ${city}.`,
    firstName: "Nombre",
    lastName: "Apellido",
    phone: "Teléfono",
    email: "Correo Electrónico",
    cityLabel: "Ciudad",
    employer: "Nombre del Empleador",
    optional: "(opcional)",
    whatHappened: "¿Qué pasó?",
    consent:
      "Acepto que Employment Law Assist me contacte sobre mi consulta. Entiendo que contactar a la firma no crea una relación abogado-cliente.",
    submit: "Obtener Mi Consulta Gratis",
    submitting: "Enviando...",
    errFirst: "Ingrese su nombre.",
    errLast: "Ingrese su apellido.",
    errPhone: "Ingrese un número de teléfono válido.",
    errEmail: "Ingrese un correo electrónico válido.",
    errCity: "Ingrese su ciudad.",
    errWhat: "Cuéntenos brevemente qué pasó.",
    errConsent: "Por favor otorgue su consentimiento para continuar.",
    genericError: "Algo salió mal. Por favor llámenos.",
  },
  disclaimer: (city) =>
    `La información en esta página es solo para fines informativos generales y no constituye asesoría legal. Contactar a Employment Law Assist no crea una relación abogado-cliente. Employment Law Assist ayuda a empleados en ${city} y no mantiene una oficina física en ${city}. Cada caso es diferente y los resultados anteriores no garantizan un resultado similar.`,
  disclaimerGeneric:
    "La información en esta página es solo para fines informativos generales y no constituye asesoría legal. Contactar a Employment Law Assist no crea una relación abogado-cliente. Cada caso es diferente y los resultados anteriores no garantizan un resultado similar.",
  footerDisclaimer:
    "La información en este sitio web es publicidad de abogados y es solo para información general. Nada aquí constituye asesoría legal para ningún caso o situación individual. Esta información no pretende crear, y su recepción o visualización no constituye, una relación abogado-cliente.",
  footerOfficeTitle: "Oficina",
  footerContactTitle: "Contáctenos",
  thankYouTitle: "Gracias — hemos recibido su solicitud",
  thankYouBody:
    "Un miembro de nuestro equipo revisará su información y se comunicará con usted. Si desea hablar con alguien ahora, llámenos directamente — estamos disponibles por teléfono 24/7.",
  thankYouNote: "Se habla inglés y español",
  switchLangLabel: "English",
};

export const COPY: Record<Lang, Copy> = { en, es };
