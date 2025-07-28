import os
import glob

def parse_mdoc_tiltangle_prior_dose(mdoc_path):
    """
    Parse mdoc file to extract TiltAngle and PriorRecordDose per tilt.
    Returns a list of tuples: (tilt_angle, prior_record_dose)
    """
    tilt_doses = []
    tilt_angle = None
    prior_dose = None

    try:
        with open(mdoc_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Warning: MDOC file not found: {mdoc_path}")
        return tilt_doses  # Return empty list, skip file later

    for line in lines:
        line = line.strip()
        if line.startswith('[ZValue'):
            tilt_angle = None
            prior_dose = None
        elif line.startswith('TiltAngle'):
            tilt_angle = float(line.split('=')[1].strip())
        elif line.startswith('PriorRecordDose'):
            prior_dose = float(line.split('=')[1].strip())
            if tilt_angle is not None and prior_dose is not None:
                tilt_doses.append((tilt_angle, prior_dose))

    return tilt_doses

def find_closest_dose(tilt_angle, tilt_doses):
    if not tilt_doses:
        return None
    closest = min(tilt_doses, key=lambda x: abs(x[0] - tilt_angle))
    return closest[1]

def update_star_file(star_file, mdoc_folder, exposure_dose):
    """
    Update one STAR file using its corresponding MDOC file from a different folder.
    """
    base_name = os.path.basename(star_file)
    tomo_base = base_name.replace('.mrc.star', '')
    mdoc_path = os.path.join(mdoc_folder, f"{tomo_base}.mdoc")

    tilt_doses = parse_mdoc_tiltangle_prior_dose(mdoc_path)
    if not tilt_doses:
        print(f"Skipping {star_file}: No valid data from {mdoc_path}")
        return

    print(f"Processing {star_file} using {mdoc_path}...")

    with open(star_file, 'r') as f:
        lines = f.readlines()

    if len(lines) < 36:
        print(f"File {star_file} is too short to contain data at line 36+")
        return

    for i in range(35, len(lines)):
        line = lines[i].strip()
        if not line or line.startswith('#'):
            continue

        cols = line.split()
        if len(cols) < 5:
            continue

        try:
            tilt_angle = float(cols[2])
        except ValueError:
            continue

        prior_dose = find_closest_dose(tilt_angle, tilt_doses)
        if prior_dose is None:
            continue

        mult = round(prior_dose / exposure_dose)
        adjusted_dose = mult * exposure_dose - exposure_dose
        if adjusted_dose < 0:
            adjusted_dose = 0.0

        cols[4] = f"{adjusted_dose:.4f}"
        lines[i] = "\t".join(cols) + "\n"

    with open(star_file, 'w') as f:
        f.writelines(lines)

    print(f"Updated file saved: {star_file}")

def update_all_star_files(star_folder, mdoc_folder, exposure_dose):
    """
    Process all star files in star_folder using matching mdoc files from mdoc_folder.
    """
    pattern = os.path.join(star_folder, '*.mrc.star')
    star_files = glob.glob(pattern)

    if not star_files:
        print("No matching star files found.")
        return

    for star_file in star_files:
        update_star_file(star_file, mdoc_folder, exposure_dose)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Update pre exposure dose in star files using matching mdoc files from a separate folder")
    parser.add_argument("star_folder", help="Folder containing .star files")
    parser.add_argument("mdoc_folder", help="Folder containing .mdoc files")
    parser.add_argument("exposure_dose", type=float, help="Exposure dose per tilt (e-/Å²)")

    args = parser.parse_args()

    update_all_star_files(args.star_folder, args.mdoc_folder, args.exposure_dose)
