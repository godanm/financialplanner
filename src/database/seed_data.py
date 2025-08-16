from database import get_db_session, FamilyMember

def seed_family_data():
    session = get_db_session()
    if not session.query(FamilyMember).first():
        family_members = [
            FamilyMember(name="You", age=50, relation="Self", education_plan=""),
            FamilyMember(name="Spouse", age=48, relation="Spouse", education_plan=""),
            FamilyMember(name="Son", age=21, relation="Child", education_plan="Medical School"),
            FamilyMember(name="Daughter", age=11, relation="Child", education_plan="College")
        ]
        session.add_all(family_members)
        session.commit()
    session.close()

if __name__ == "__main__":
    seed_family_data()