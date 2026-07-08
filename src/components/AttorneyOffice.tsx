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
    <section className="bg-white px-5 py-14">
      <div className="mx-auto max-w-4xl">
        <h2 className="text-center text-[26px] font-extrabold text-[var(--navy)] sm:text-3xl">
          {title}
        </h2>
        <div className="mx-auto mt-3 h-1 w-12 rounded-full bg-[var(--gold)]" />

        <div className="mt-10 flex flex-col items-center gap-6 sm:flex-row sm:items-start">
          <div className="w-full max-w-[280px] shrink-0 overflow-hidden rounded-2xl border-2 border-slate-200 shadow-md">
            <Image
              src="/images/attorney-kasim.png"
              alt={`${name}, ${role}`}
              width={600}
              height={600}
              className="h-auto w-full object-cover"
              sizes="280px"
            />
          </div>
          <div className="text-center sm:text-left">
            <p className="text-2xl font-bold text-[var(--navy)]">{name}</p>
            <p className="mt-1 text-sm font-semibold uppercase tracking-wide text-[var(--gold)]">
              {role}
            </p>
            <p className="mt-4 text-[17px] leading-relaxed text-slate-700">{bio}</p>
          </div>
        </div>

        <div className="mt-10 grid gap-5 sm:grid-cols-2">
          <figure className="overflow-hidden rounded-2xl border-2 border-slate-200 shadow-sm">
            <Image
              src="/images/office-exterior.png"
              alt="Employment Law Assist office building in Woodland Hills, California"
              width={1000}
              height={667}
              className="h-48 w-full object-cover sm:h-52"
              sizes="(max-width: 640px) 100vw, 50vw"
            />
            <figcaption className="bg-slate-50 px-4 py-2.5 text-center text-sm text-slate-500">
              {officeCaption}
            </figcaption>
          </figure>
          <figure className="overflow-hidden rounded-2xl border-2 border-slate-200 shadow-sm">
            <Image
              src="/images/team-working.png"
              alt="The Employment Law Assist team working on a case"
              width={1000}
              height={667}
              className="h-48 w-full object-cover sm:h-52"
              sizes="(max-width: 640px) 100vw, 50vw"
            />
            <figcaption className="bg-slate-50 px-4 py-2.5 text-center text-sm text-slate-500">
              {teamCaption}
            </figcaption>
          </figure>
        </div>
      </div>
    </section>
  );
}
