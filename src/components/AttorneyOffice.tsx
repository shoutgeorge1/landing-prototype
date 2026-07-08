import Image from "next/image";

interface AttorneyOfficeProps {
  title: string;
  name: string;
  role: string;
  bio: string;
  officeCaption: string;
  teamCaption: string;
}

export function AttorneyOffice({
  title,
  name,
  role,
  bio,
  officeCaption,
  teamCaption,
}: AttorneyOfficeProps) {
  return (
    <section className="bg-white px-6 py-16">
      <div className="mx-auto max-w-6xl">
        <h2 className="text-center text-2xl font-bold text-[var(--navy)] sm:text-3xl">{title}</h2>

        <div className="mt-10 grid items-center gap-8 md:grid-cols-[minmax(0,320px)_1fr]">
          <div className="mx-auto w-full max-w-xs overflow-hidden rounded-2xl border border-slate-200">
            <Image
              src="/images/attorney-kasim.png"
              alt={`${name}, ${role}`}
              width={600}
              height={600}
              className="h-auto w-full object-cover"
              sizes="(max-width: 768px) 80vw, 320px"
            />
          </div>
          <div>
            <p className="text-xl font-bold text-[var(--navy)]">{name}</p>
            <p className="mt-1 text-sm font-semibold uppercase tracking-wide text-[var(--gold)]">
              {role}
            </p>
            <p className="mt-4 text-base leading-relaxed text-slate-700">{bio}</p>
          </div>
        </div>

        <div className="mt-10 grid gap-6 sm:grid-cols-2">
          <figure className="overflow-hidden rounded-2xl border border-slate-200">
            <Image
              src="/images/office-exterior.png"
              alt="Employment Law Assist office building in Woodland Hills, California"
              width={1000}
              height={667}
              className="h-56 w-full object-cover"
              sizes="(max-width: 640px) 100vw, 50vw"
            />
            <figcaption className="bg-slate-50 px-4 py-2 text-center text-xs text-slate-500">
              {officeCaption}
            </figcaption>
          </figure>
          <figure className="overflow-hidden rounded-2xl border border-slate-200">
            <Image
              src="/images/team-working.png"
              alt="The Employment Law Assist team working on a case"
              width={1000}
              height={667}
              className="h-56 w-full object-cover"
              sizes="(max-width: 640px) 100vw, 50vw"
            />
            <figcaption className="bg-slate-50 px-4 py-2 text-center text-xs text-slate-500">
              {teamCaption}
            </figcaption>
          </figure>
        </div>
      </div>
    </section>
  );
}
