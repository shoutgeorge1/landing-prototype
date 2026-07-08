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
  trustPoints: string[];
  ctaPrimary: string;
  ctaCall: string;
  trustBadgesTitle: string;
  problemTitle: (city: string) => string;
  problemBody: (city: string) => string[];
  noWinTitle: string;
  noWinBody: string[];
  practiceTitle: string;
  practiceIntro: (city: string) => string;
  practiceAreas: string[];
  whyUsTitle: string;
  whyUs: string[];
  whyUsNote: string;
  stepsTitle: string;
  steps: Step[];
  testimonialsTitle: string;
  testimonialsIntro: string;
  finalTitle: string;
  finalBody: (city: string) => string;
  finalNote: string;
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
    `Employment Law Assist helps employees in ${city}, California with wrongful termination, discrimination, retaliation, harassment, and wage claims. No win, no fee. Free, confidential consultation.`,
  headline: (city) => `Employment Lawyers Serving ${city} Employees`,
  subheadline:
    "Compassionate attorneys fighting for California employees — wrongful termination, workplace discrimination, retaliation, harassment, wage issues, and meal/rest break violations.",
  trustPoints: ["Hablamos Español", "100% Free Consultation", "Available 24/7 By Phone"],
  ctaPrimary: "Request a Free Consultation",
  ctaCall: `Call Now: ${FIRM.phoneDisplay}`,
  trustBadgesTitle: "Recognized & Trusted",
  problemTitle: (city) => `Facing a workplace problem in ${city}?`,
  problemBody: (city) => [
    `If you're dealing with a serious problem at work, you don't have to face it alone. Employment Law Assist helps employees in ${city} understand their rights under California law.`,
    "Whether you were fired, harassed, discriminated against, or denied pay you earned, a free consultation is the fastest way to learn where you stand.",
  ],
  noWinTitle: "No Win, No Fee — 100% Risk-Free",
  noWinBody: [
    "We will handle your case on a contingency fee basis, which means you don't pay a thing unless we win or settle your case.",
    "We pay all case costs and expenses from start to finish. You pay $0 out of pocket. If your case is unsuccessful for any reason, you owe us nothing.",
  ],
  practiceTitle: "Our Practice Areas",
  practiceIntro: (city) =>
    `We help employees in ${city} across a full range of California workplace claims.`,
  practiceAreas: [
    "Wrongful Termination",
    "Meal & Rest Break Violations",
    "Retaliation",
    "Discrimination",
    "Workers' Compensation",
    "Harassment",
  ],
  whyUsTitle: "Why Employment Law Assist?",
  whyUs: [
    "A premier employment law firm that aggressively represents employees.",
    "Compassionate attorneys dedicated to enforcing employees' rights in the workplace.",
    "Extensive knowledge across every area of employment law — wage & hour, workers' compensation, wrongful termination, retaliation, discrimination, and harassment.",
  ],
  whyUsNote:
    "If your current or former employer has wronged you in any way, you may be entitled to compensation. Contact us for a free and confidential consultation.",
  stepsTitle: "3 Easy Steps to Get Help",
  steps: [
    {
      title: "Call or fill out the form",
      body: `Call ${FIRM.phoneDisplay} or complete the form on this page.`,
    },
    { title: "Speak with us", body: "Speak with us to evaluate your claim." },
    { title: "Get help with your claim", body: "We pursue the compensation you deserve." },
  ],
  testimonialsTitle: "Client Success Stories",
  testimonialsIntro: "Real reviews from people we've helped.",
  finalTitle: "Talk to someone about your situation today",
  finalBody: (city) =>
    `Call now or request a free, confidential consultation. Serving employees in ${city} across California.`,
  finalNote: "Available 24/7 by phone. Hablamos Español.",
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
    `Employment Law Assist ayuda a empleados en ${city}, California con despido injustificado, discriminación, represalias, acoso y reclamos de salario. Sin ganar, sin pagar. Consulta gratis y confidencial.`,
  headline: (city) => `Abogados Laborales que Ayudan a Empleados en ${city}`,
  subheadline:
    "Abogados compasivos que luchan por los empleados de California — despido injustificado, discriminación laboral, represalias, acoso, problemas de salario y violaciones de descansos o comida.",
  trustPoints: ["Hablamos Español", "Consulta 100% Gratis", "Disponible por Teléfono 24/7"],
  ctaPrimary: "Solicite una Consulta Gratis",
  ctaCall: `Llame Ahora: ${FIRM.phoneDisplay}`,
  trustBadgesTitle: "Reconocidos y de Confianza",
  problemTitle: (city) => `¿Tiene un problema laboral en ${city}?`,
  problemBody: (city) => [
    `Si enfrenta un problema serio en el trabajo, no tiene que hacerlo solo. Employment Law Assist ayuda a empleados en ${city} a entender sus derechos bajo la ley de California.`,
    "Ya sea que lo hayan despedido, acosado, discriminado o negado el pago que ganó, una consulta gratis es la forma más rápida de conocer sus opciones.",
  ],
  noWinTitle: "Sin Ganar, Sin Pagar — 100% Sin Riesgo",
  noWinBody: [
    "Manejamos su caso con honorarios de contingencia, lo que significa que usted no paga nada a menos que ganemos o resolvamos su caso.",
    "Nosotros cubrimos todos los costos y gastos del caso de principio a fin. Usted paga $0 de su bolsillo. Si su caso no tiene éxito por cualquier razón, usted no nos debe nada.",
  ],
  practiceTitle: "Nuestras Áreas de Práctica",
  practiceIntro: (city) =>
    `Ayudamos a empleados en ${city} con una amplia gama de reclamos laborales en California.`,
  practiceAreas: [
    "Despido Injustificado",
    "Violaciones de Descanso y Comida",
    "Represalias",
    "Discriminación",
    "Compensación Laboral",
    "Acoso",
  ],
  whyUsTitle: "¿Por Qué Employment Law Assist?",
  whyUs: [
    "Una firma líder en derecho laboral que representa agresivamente a los empleados.",
    "Abogados compasivos dedicados a hacer valer los derechos de los empleados en el trabajo.",
    "Amplio conocimiento en todas las áreas del derecho laboral: salario y horas, compensación laboral, despido injustificado, represalias, discriminación y acoso.",
  ],
  whyUsNote:
    "Si su empleador actual o anterior le ha perjudicado de alguna manera, usted podría tener derecho a una compensación. Contáctenos para una consulta gratis y confidencial.",
  stepsTitle: "3 Pasos Sencillos para Recibir Ayuda",
  steps: [
    {
      title: "Llame o complete el formulario",
      body: `Llame al ${FIRM.phoneDisplay} o complete el formulario en esta página.`,
    },
    { title: "Hable con nosotros", body: "Hable con nosotros para evaluar su reclamo." },
    { title: "Reciba ayuda con su reclamo", body: "Buscamos la compensación que usted merece." },
  ],
  testimonialsTitle: "Historias de Éxito de Clientes",
  testimonialsIntro:
    "Reseñas reales de personas a las que hemos ayudado. Las reseñas se muestran en su idioma original (inglés).",
  finalTitle: "Hable con alguien sobre su situación hoy",
  finalBody: (city) =>
    `Llame ahora o solicite una consulta gratis y confidencial. Ayudamos a empleados en ${city} en todo California.`,
  finalNote: "Disponible por teléfono 24/7. Hablamos Español.",
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
